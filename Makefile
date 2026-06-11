.PHONY: validate validate-examples validate-evidence-fabric-contracts

validate: validate-examples validate-evidence-fabric-contracts
	@echo "OK: validate"

validate-examples:
	python3 scripts/validate_examples.py

validate-evidence-fabric-contracts:
	python3 scripts/validate_exodus_evidence_fabric_all.py
