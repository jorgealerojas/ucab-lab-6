from __future__ import annotations

import re
import unittest
from pathlib import Path


ROOT = Path(__file__).parents[1]
README = (ROOT / "README.md").read_text(encoding="utf-8")
GUIDE = (ROOT / "LAB_GUIDE.md").read_text(encoding="utf-8")


class DocumentationContractTests(unittest.TestCase):
    def test_readme_routes_execution_to_single_guide(self) -> None:
        self.assertIn("Siga [LAB_GUIDE.md]", README)
        self.assertNotIn("./scripts/deploy-lab.sh", README)
        self.assertNotIn("git clone https://", README)

    def test_guide_has_explicit_questions_and_report(self) -> None:
        self.assertIn("## Preguntas para el informe", GUIDE)
        self.assertIn("## Informe a entregar", GUIDE)
        question_section = GUIDE.split("## Preguntas para el informe", 1)[1].split(
            "\n## ", 1
        )[0]
        self.assertEqual(len(re.findall(r"^\d+\. ", question_section, re.MULTILINE)), 7)

    def test_shell_blocks_contain_one_command(self) -> None:
        blocks = re.findall(r"```bash\n(.*?)\n```", GUIDE, re.DOTALL)
        self.assertTrue(blocks)
        for block in blocks:
            logical_lines = [
                line
                for line in block.splitlines()
                if line.strip() and not line.lstrip().startswith("#")
            ]
            self.assertEqual(
                len(logical_lines),
                1,
                msg=f"El bloque debe contener un solo comando: {block!r}",
            )

    def test_material_is_limited_to_first_week(self) -> None:
        self.assertIn("solo la Semana 1", README)
        self.assertIn("**Semana:** 1 de 2", GUIDE)


if __name__ == "__main__":
    unittest.main()
