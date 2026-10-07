.PHONY: test verify benchmark live bombe all
all: verify
verify:
	python3 experiments/run_all.py
test:
	pytest -q
benchmark:
	python3 experiments/benchmark.py
live:
	python3 experiments/verify_live.py
bombe:
	python3 experiments/bombe_demo.py --seed 7
