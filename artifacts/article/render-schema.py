"""Render a readable subset of Anchor's implemented graph relationships."""
from pathlib import Path
import re
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[2]
OUT = Path(__file__).resolve().parent
FONT = Path('C:/Windows/Fonts/arial.ttf')
BOLD = Path('C:/Windows/Fonts/arialbd.ttf')
GROUPS = [
    ('operational-schema.png', 'FalkorDB: the operational network', [
        ('Contract', 'APPROVES', 'Supplier', 'DEPENDS_ON', 'Supplier / upstream'),
        ('Supplier', 'OPERATES', 'Facility', 'LOCATED_AT', 'Location'),
        ('Supplier', 'SUPPLIES', 'Product', '<REQUIRES', 'Order'),
        ('Inventory', 'STORES', 'Product', '', ''),
        ('Inventory', 'HELD_AT', 'Facility', '', ''),
        ('Order', 'DELIVERED_TO', 'Customer', '', ''),
    ], 'SUPPLIES carries capacity, price, currency, lead time, availability and provenance.'),
    ('decision-schema.png', 'FalkorDB: the decision and evidence trail', [
        ('RecoveryPlan', 'MITIGATES', 'Incident', 'AFFECTS', 'Affected entity'),
        ('RecoveryPlan', 'CONTAINS', 'Action', 'PRODUCED', 'ExecutionReceipt'),
        ('Incident', 'SUPPORTED_BY', 'Evidence', '', ''),
        ('Action', 'JUSTIFIED_BY', 'Evidence', '', ''),
    ], 'Scenario.version is captured by plans and checked before execution. ERP state lives in SQLite.'),
]

def render(filename, title, rows, note):
    image = Image.new('RGB', (2200, 1180), '#071c2c')
    draw = ImageDraw.Draw(image)
    def font(size, bold=False):
        return ImageFont.truetype(str(BOLD if bold else FONT), size)
    draw.text((90, 65), title, font=font(62, True), fill='#fff7e8')
    draw.text((90, 155), 'Implemented relationship subset | arrows follow stored Cypher direction', font=font(30), fill='#a4c4cf')
    starts = [90, 845, 1600]
    width, height = 490, 95
    step = 128 if len(rows) == 6 else 170
    for row_index, row in enumerate(rows):
        y = 245 + row_index * step
        for col, text in enumerate(row[::2]):
            if not text:
                continue
            x = starts[col]
            draw.rounded_rectangle((x, y, x + width, y + height), 16, fill='#163448', outline='#63cdda', width=3)
            box = draw.textbbox((0, 0), text, font=font(34, True))
            draw.text((x + (width - (box[2] - box[0])) / 2, y + 27), text, font=font(34, True), fill='#fff7e8')
        for col, relationship in enumerate((row[1], row[3])):
            if not relationship:
                continue
            left = starts[col] + width + 15
            right = starts[col + 1] - 15
            cy = y + height / 2
            reverse = relationship.startswith('<')
            label = relationship.lstrip('<')
            draw.line((left, cy, right, cy), fill='#63cdda', width=4)
            tip, back = (left, left + 17) if reverse else (right, right - 17)
            draw.polygon([(tip, cy), (back, cy - 10), (back, cy + 10)], fill='#63cdda')
            bounds = draw.textbbox((0, 0), label, font=font(23, True))
            draw.text(((left + right - (bounds[2] - bounds[0])) / 2, y + 7), label, font=font(23, True), fill='#eabf66')
    draw.text((90, 1050), note, font=font(28), fill='#fff7e8')
    draw.text((90, 1100), 'Repeated labels denote the same node type. Schematic, not a live database screenshot. All commercial data is synthetic.', font=font(26), fill='#a4c4cf')
    image.save(OUT / filename)

if __name__ == '__main__':
    graph_source = (ROOT / 'src/anchor/graph.py').read_text(encoding='utf-8')
    for filename, title, rows, note in GROUPS:
        for row in rows:
            for relationship in (row[1], row[3]):
                if relationship:
                    assert re.search(r'"' + relationship.lstrip('<') + r'"\s*:', graph_source), relationship
        render(filename, title, rows, note)
        with Image.open(OUT / filename) as check:
            assert check.size == (2200, 1180)
    print('Rendered and checked two schema diagrams against graph.py relationship templates.')
