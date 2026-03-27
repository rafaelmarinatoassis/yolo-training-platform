import json
import os
import tempfile
import unittest
import uuid

from PIL import Image

from app import create_app


class TestMvpIntegration(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = create_app()
        cls.client = cls.app.test_client()

        # Patch heavy background operations for fast/consistent integration tests.
        import app.routes.trainings as trainings_routes
        import app.routes.tests as tests_routes

        cls._trainings_routes = trainings_routes
        cls._tests_routes = tests_routes
        cls._orig_start_training = trainings_routes.trainer.start_training
        cls._orig_run_inference = tests_routes.inference.run_inference

        trainings_routes.trainer.start_training = lambda training_id: True

        def fake_inference(model_path, source_type, input_path, test_id, **kwargs):
            return {
                'success': True,
                'results': {'type': source_type, 'detection_count': 0},
                'output_dir': os.path.join('data', 'tests', str(test_id)),
            }

        tests_routes.inference.run_inference = fake_inference

    @classmethod
    def tearDownClass(cls):
        cls._trainings_routes.trainer.start_training = cls._orig_start_training
        cls._tests_routes.inference.run_inference = cls._orig_run_inference

    def test_stats_endpoints(self):
        for route in ('/api/datasets/stats', '/api/trainings/stats', '/api/system/info'):
            response = self.client.get(route)
            self.assertEqual(response.status_code, 200, f'Failed route: {route}')

    def test_models_endpoints(self):
        check_missing = self.client.post('/api/models/check', json={'model_name': 'yolov8n.pt'})
        self.assertEqual(check_missing.status_code, 200)
        self.assertIn('exists', check_missing.json)
        self.assertIn('downloadable', check_missing.json)

        list_models = self.client.get('/api/models/list')
        self.assertEqual(list_models.status_code, 200)
        self.assertIn('models', list_models.json)

        with tempfile.TemporaryDirectory() as tmpdir:
            local_model = os.path.join(tmpdir, 'local_model.pt')
            with open(local_model, 'wb') as file_obj:
                file_obj.write(b'LOCAL_PT')

            download_existing = self.client.post(
                '/api/models/download',
                json={'model_name': local_model},
            )
            self.assertEqual(download_existing.status_code, 200)
            self.assertTrue(download_existing.json.get('success'))

    def test_dataset_training_and_tests_flow(self):
        # Build temporary files for upload.
        with tempfile.TemporaryDirectory() as tmpdir:
            image_path = os.path.join(tmpdir, 'sample.jpg')
            label_path = os.path.join(tmpdir, 'sample.txt')
            fake_model_path = os.path.join(tmpdir, 'fake_model.pt')

            Image.new('RGB', (32, 32), (255, 0, 0)).save(image_path, format='JPEG')
            with open(label_path, 'w', encoding='utf-8') as file_obj:
                file_obj.write('0 0.5 0.5 0.4 0.4\n')
            with open(fake_model_path, 'wb') as file_obj:
                file_obj.write(b'FAKE_PT')

            dataset_name = f"mvp_ds_{uuid.uuid4().hex[:8]}"

            with (
                open(image_path, 'rb') as train_image,
                open(label_path, 'rb') as train_label,
                open(image_path, 'rb') as val_image,
                open(label_path, 'rb') as val_label,
            ):
                create_dataset = self.client.post(
                    '/api/datasets',
                    data={
                        'name': dataset_name,
                        'classes': json.dumps(['objeto']),
                        'train_images': train_image,
                        'train_labels': train_label,
                        'val_images': val_image,
                        'val_labels': val_label,
                    },
                    content_type='multipart/form-data',
                )

            self.assertEqual(create_dataset.status_code, 201)
            dataset_id = create_dataset.json['dataset']['id']

            list_datasets = self.client.get('/api/datasets?search=mvp_ds&sort=name')
            self.assertEqual(list_datasets.status_code, 200)
            self.assertGreaterEqual(list_datasets.json['total'], 1)

            create_training = self.client.post(
                '/api/trainings',
                json={
                    'dataset_id': dataset_id,
                    'task_type': 'detect',
                    'model_version': 'n',
                    'epochs': 1,
                    'batch_size': 1,
                    'img_size': 320,
                    'lr': 0.01,
                },
            )
            self.assertEqual(create_training.status_code, 201)
            training_id = create_training.json['training_id']

            get_training = self.client.get(f'/api/trainings/{training_id}')
            self.assertEqual(get_training.status_code, 200)

            with open(image_path, 'rb') as image_file:
                create_test = self.client.post(
                    '/api/tests',
                    data={
                        'model_path': fake_model_path,
                        'source_type': 'image',
                        'image_file': image_file,
                    },
                    content_type='multipart/form-data',
                )

            self.assertEqual(create_test.status_code, 201)
            test_id = create_test.json['test']['id']

            get_test = self.client.get(f'/api/tests/{test_id}')
            self.assertEqual(get_test.status_code, 200)

            delete_training = self.client.delete(f'/api/trainings/{training_id}')
            self.assertEqual(delete_training.status_code, 200)

            delete_dataset = self.client.delete(f'/api/datasets/{dataset_id}')
            self.assertEqual(delete_dataset.status_code, 200)


if __name__ == '__main__':
    unittest.main()
