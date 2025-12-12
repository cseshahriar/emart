# author: @cseshahriar
.PHONY: help test lint format format-check coverage check all \
        migrations migrate start superuser install update \
        clear-pycache collectstatic makemessages compilemessages \
        clean test-watch shell

DJANGO=python manage.py
PYTHON=python

help:
	@echo "Available commands:"
	@echo ""
	@echo "🐍 Development:"
	@echo "  make start     - Start development server"
	@echo "  make shell     - Open Django shell"
	@echo "  make migrations- Create new migrations"
	@echo "  make migrate   - Apply migrations"
	@echo "  make superuser - Create superuser"
	@echo ""
	@echo "🧪 Testing:"
	@echo "  make test      - Run all tests"
	@echo "  make test-watch- Run tests on file change"
	@echo "  make coverage  - Run tests with coverage"
	@echo ""
	@echo "📏 Code Quality:"
	@echo "  make lint      - Run flake8 linting"
	@echo "  make format    - Format code with black/isort"
	@echo "  make format-check - Check formatting without changes"
	@echo "  make check     - Run all checks (format + lint + test)"
	@echo "  make all       - Run everything"
	@echo ""
	@echo "🛠️  Maintenance:"
	@echo "  make install   - Install dependencies"
	@echo "  make update    - Update dependencies"
	@echo "  make clean     - Remove cache files"
	@echo "  make clear-pycache - Remove __pycache__ directories"
	@echo ""
	@echo "🌐 Deployment:"
	@echo "  make collectstatic - Collect static files"
	@echo "  make makemessages - Create translation files"
	@echo "  make compilemessages - Compile translation files"

# 🧪 Testing
test:
	$(DJANGO) test users --verbosity=2

test-all:
	$(DJANGO) test --verbosity=2

test-watch:
	find . -name "*.py" | entr -c $(DJANGO) test users --verbosity=2

test-coverage:
	coverage run --source='.' $(DJANGO) test users
	coverage report
	coverage html

# 📏 Code Quality
lint:
	flake8 . --count --select=E9,F63,F7,F82 --show-source --statistics
	@echo "---"
	flake8 . --count --exit-zero --max-complexity=10 --max-line-length=127 --statistics

format:
	black .
	isort .

format-check:
	black . --check
	isort . --check-only

coverage:
	coverage erase
	coverage run --source='.' $(DJANGO) test users
	coverage report
	coverage html -d htmlcov

# ✅ Combined checks
check: format-check lint test

all: format lint coverage

# 🐍 Development
migrations:
	$(DJANGO) makemigrations

migrate:
	$(DJANGO) migrate

start:
	$(DJANGO) runserver 0.0.0.0:8000

superuser:
	$(DJANGO) createsuperuser

shell:
	$(DJANGO) shell_plus --ipython

# 📦 Dependencies
install:
	pip install -r requirements/base.txt

update:
	pip install --upgrade -r requirements/base.txt

# 🧹 Cleanup
clean:
	find . -type d -name '__pycache__' -exec rm -rf {} +
	find . -type f -name '*.pyc' -delete
	find . -type f -name '*.pyo' -delete
	find . -type f -name '*~' -delete
	find . -type f -name '*.swp' -delete
	find . -type d -name '.pytest_cache' -exec rm -rf {} +
	find . -type d -name '.coverage' -delete
	find . -type d -name 'htmlcov' -exec rm -rf {} +
	find . -type d -name '*.egg-info' -exec rm -rf {} +
	find . -type d -name '.mypy_cache' -exec rm -rf {} +

clear-pycache:
	find . -type d -name '__pycache__' -exec rm -rf {} +
	find . -type f -name '*.pyc' -delete
	find . -type f -name '*.pyo' -delete

# 🌐 Deployment
collectstatic:
	$(DJANGO) collectstatic --noinput

makemessages:
	$(DJANGO) makemessages -l en

compilemessages:
	$(DJANGO) compilemessages

# 🔧 Database
resetdb:
	@echo "⚠️  This will delete your database! Are you sure? [y/N]" && read ans && [ $${ans:-N} = y ]
	rm -f db.sqlite3
	$(DJANGO) migrate
	$(DJANGO) createsuperuser

# 📊 Requirements
requirements:
	pip freeze > requirements.txt

requirements-dev:
	pip freeze > requirements/dev.txt
