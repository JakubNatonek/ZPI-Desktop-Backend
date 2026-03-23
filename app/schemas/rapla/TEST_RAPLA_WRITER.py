import tempfile
import unittest
import xml.etree.ElementTree as ET
from pathlib import Path

from app.schemas.rapla.rapla_namespaces import RAPLA_NS, RAPLA_VERSION
from app.schemas.rapla.schema_rapla_file import RaplaData


class TestRaplaWriter(unittest.TestCase):
	def test_to_xml_contains_root_and_version(self) -> None:
		data = RaplaData()

		xml_text = data.to_xml()
		root = ET.fromstring(xml_text)

		self.assertTrue(xml_text.startswith("<?xml"))
		self.assertEqual(root.tag, f"{{{RAPLA_NS}}}data")
		self.assertEqual(root.attrib.get("version"), RAPLA_VERSION)
		self.assertIn("xmlns:rapla=\"http://rapla.sourceforge.net/rapla\"", xml_text)
		self.assertIsNotNone(root.find(f"{{{RAPLA_NS}}}users"))
		self.assertIsNotNone(root.find(f"{{{RAPLA_NS}}}users/{{{RAPLA_NS}}}user"))

	def test_save_to_file_writes_xml(self) -> None:
		data = RaplaData()

		with tempfile.TemporaryDirectory() as tmp_dir:
			target = Path(tmp_dir) / "rapla.xml"
			data.save_to_file(str(target))

			self.assertTrue(target.exists())
			file_content = target.read_text(encoding="utf-8")
			self.assertEqual(file_content, data.to_xml())

if __name__ == "__main__":
	unittest.main()
