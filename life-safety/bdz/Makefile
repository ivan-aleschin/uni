# Сборка отчёта: report.md -> report.docx (оформление из reference.docx).
# Нужны pandoc и python3 из flake.nix в корне репозитория.

report.docx: report.md reference.docx
	pandoc report.md --from markdown --reference-doc=reference.docx -o report.docx

reference.docx: make_reference.py
	python3 make_reference.py

clean:
	rm -f report.docx

.PHONY: clean
