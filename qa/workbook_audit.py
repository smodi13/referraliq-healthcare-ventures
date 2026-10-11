"""Read-only OOXML integrity audit using Python standard library, no workbook edits."""
import zipfile,xml.etree.ElementTree as ET,math,pathlib,re,json
P=pathlib.Path(__file__).resolve().parents[1]
FILE=P/'Pilot_ROI_and_Venture_Model.xlsx';NS={'x':'http://schemas.openxmlformats.org/spreadsheetml/2006/main'}
fixt=json.loads((P/'model_fixtures.json').read_text())['scenarios']
with zipfile.ZipFile(FILE) as z:
 sheets=[p for p in z.namelist() if re.fullmatch(r'xl/worksheets/sheet\d+\.xml',p)]
 formulas=0;errors=[];xml_roots={}
 for path in sheets:
  root=ET.fromstring(z.read(path));xml_roots[path]=root
  formulas+=len(root.findall('.//x:f',NS))
  for c in root.findall('.//x:c',NS):
   v=c.find('x:v',NS)
   if v is not None and v.text and v.text.startswith(('#REF!','#DIV/0!','#VALUE!','#NAME?','#N/A')):errors.append((path,c.attrib.get('r'),v.text))
 assert len(sheets)==14,(len(sheets),'expected 14')
 assert formulas>=275,('too few formulas',formulas)
 assert not errors,errors
 def cached(sheet,ref):
  root=xml_roots[f'xl/worksheets/sheet{sheet}.xml'];c=root.find(f'.//x:c[@r="{ref}"]',NS); assert c is not None,(sheet,ref)
  v=c.find('x:v',NS);assert v is not None and v.text,(sheet,ref,'no calculated cached value')
  return float(v.text)
 for col,name in zip('BCD',['Downside','Base','Upside']):
  t=fixt[name]
  for sheet,ref,exp in [(4,col+'20',t['pilot_net']),(5,col+'19',t['runrate_net']),(5,col+'27',t['first_year_net']),(8,col+'22',t['venture_moic']),(8,col+'23',t['venture_irr'])]:
   got=cached(sheet,ref);assert math.isclose(got,exp,abs_tol=1e-6,rel_tol=1e-10),(name,sheet,ref,got,exp)
 print(f'PASS: {len(sheets)} sheets, {formulas} cached formulas, no Excel errors, 15/15 financial output parity checks')
