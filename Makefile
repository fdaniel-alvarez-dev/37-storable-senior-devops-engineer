.PHONY: setup demo demo-offline up down logs seed backup restore check test test-demo test-production clean

demo: up seed check backup restore
	@echo "Demo complete. Try: make logs"

demo-offline:
	python3 pipelines/pipeline_demo.py

up:
	docker compose up -d --build

down:
	docker compose down -v

logs:
	docker compose logs -f --tail=200

check:
	bash scripts/check_replication.sh

seed:
	bash scripts/seed_demo_data.sh

backup:
	bash scripts/backup.sh

restore:
	bash scripts/restore.sh

test: test-demo

test-demo:
	TEST_MODE=demo python3 tests/run_tests.py

test-production:
	TEST_MODE=production PRODUCTION_TESTS_CONFIRM=1 python3 tests/run_tests.py

clean:
	rm -rf artifacts data/processed
