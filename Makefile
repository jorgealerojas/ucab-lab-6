.PHONY: test shellcheck cfn-lint validate

test:
	python3 -m unittest discover -s tests -p 'test_*.py' -v

shellcheck:
	shellcheck -x scripts/*.sh

cfn-lint:
	cfn-lint infra/lab-stack.yaml

validate: test shellcheck cfn-lint
