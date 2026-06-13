from __future__ import annotations

import unittest
from variables import detect_variables, build_fill_form, fill_variables, validate_template


class VariableDetectionTests(unittest.TestCase):
    def test_detect_single_variable(self):
        text = "Hola {{nombre}}, bienvenido"
        result = detect_variables(text)
        self.assertEqual(result, ["nombre"])

    def test_detect_multiple_variables(self):
        text = "{{proyecto}} usa {{lenguaje}} en {{sistema}}"
        result = detect_variables(text)
        self.assertEqual(result, ["lenguaje", "proyecto", "sistema"])

    def test_no_variables(self):
        text = "Este texto no tiene variables"
        result = detect_variables(text)
        self.assertEqual(result, [])

    def test_duplicate_variables(self):
        text = "{{nombre}} y {{nombre}} otra vez"
        result = detect_variables(text)
        self.assertEqual(result, ["nombre"])

    def test_empty_text(self):
        self.assertEqual(detect_variables(""), [])


class VariableFillTests(unittest.TestCase):
    def test_fill_single_variable(self):
        text = "Hola {{nombre}}"
        result = fill_variables(text, {"nombre": "Mundo"})
        self.assertEqual(result, "Hola Mundo")

    def test_fill_multiple_variables(self):
        text = "{{proyecto}} usa {{lenguaje}}"
        result = fill_variables(text, {"proyecto": "MiApp", "lenguaje": "Python"})
        self.assertEqual(result, "MiApp usa Python")

    def test_fill_missing_variable_non_strict(self):
        text = "Hola {{nombre}}, bienvenido a {{lugar}}"
        result = fill_variables(text, {"nombre": "Ana"})
        self.assertEqual(result, "Hola Ana, bienvenido a {{lugar}}")

    def test_fill_missing_variable_strict(self):
        text = "Hola {{nombre}}, bienvenido a {{lugar}}"
        with self.assertRaises(ValueError):
            fill_variables(text, {"nombre": "Ana"}, strict=True)

    def test_fill_empty_values(self):
        text = "Hola {{nombre}}"
        result = fill_variables(text, {"nombre": ""})
        # Empty string replaces the variable with empty
        self.assertEqual(result, "Hola ")


class VariableFormTests(unittest.TestCase):
    def test_build_form_detects_variables(self):
        text = "Proyecto: {{nombre}}, Lenguaje: {{lang}}"
        form = build_fill_form(text)
        self.assertIn("nombre", form.variables)
        self.assertIn("lang", form.variables)

    def test_form_complete_when_all_filled(self):
        text = "{{a}} y {{b}}"
        form = build_fill_form(text)
        form.set_value("a", "1")
        form.set_value("b", "2")
        self.assertTrue(form.is_complete())

    def test_form_incomplete_when_empty(self):
        text = "{{a}} y {{b}}"
        form = build_fill_form(text)
        # By default variables are not required, so form is "complete"
        # Test with required override
        from variables import VariableDefinition
        form2 = build_fill_form(text, overrides={"a": VariableDefinition(name="a", required=True)})
        self.assertFalse(form2.is_complete())

    def test_form_unfilled_list(self):
        text = "{{a}} y {{b}}"
        form = build_fill_form(text)
        form.set_value("a", "1")
        self.assertEqual(form.unfilled(), ["b"])


class TemplateValidationTests(unittest.TestCase):
    def test_valid_template(self):
        result = validate_template("Hola {{nombre}}")
        self.assertTrue(result["valid"])
        self.assertEqual(result["variables"], ["nombre"])

    def test_empty_template(self):
        result = validate_template("")
        self.assertFalse(result["valid"])
        self.assertIn("empty_template", result["errors"])

    def test_no_variables_template(self):
        result = validate_template("Texto sin variables")
        self.assertTrue(result["valid"])
        self.assertEqual(result["variables"], [])
