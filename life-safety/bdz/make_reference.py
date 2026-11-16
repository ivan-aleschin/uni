"""Собирает reference.docx — шаблон оформления для pandoc.

Берём стандартный reference.docx из pandoc и заменяем в нём стили, поля страницы
и нижний колонтитул: Times New Roman 14 pt, полуторный интервал, абзацный отступ
1,25 см, поля 30/15/20/20 мм, таблицы с рамками, номер страницы внизу по центру
(на титульном листе номера нет), каждый заголовок 1-го уровня — с новой страницы.
Запуск: python3 make_reference.py  (вызывается из Makefile).
"""

import io
import re
import subprocess
import zipfile

W = 'xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main"'
FONT = '<w:rFonts w:ascii="Times New Roman" w:hAnsi="Times New Roman" w:eastAsia="Times New Roman" w:cs="Times New Roman"/>'


def pstyle(sid, name, ppr="", rpr="", based="Normal", extra=""):
    return (f'<w:style w:type="paragraph" w:customStyle="1" w:styleId="{sid}">'
            f'<w:name w:val="{name}"/><w:basedOn w:val="{based}"/>{extra}'
            f'<w:pPr>{ppr}</w:pPr><w:rPr>{rpr}</w:rPr></w:style>')


def heading(level, size, before, after, center=False, new_page=False):
    jc = '<w:jc w:val="center"/>' if center else '<w:jc w:val="left"/>'
    brk = '<w:pageBreakBefore/>' if new_page else ''
    return pstyle(
        f"Heading{level}", f"heading {level}",
        ppr=(f'{brk}<w:keepNext/><w:keepLines/><w:spacing w:before="{before}" w:after="{after}" w:line="240" w:lineRule="auto"/>'
             f'<w:ind w:firstLine="0"/>{jc}<w:outlineLvl w:val="{level - 1}"/>'),
        rpr=f'<w:b/><w:sz w:val="{size}"/><w:szCs w:val="{size}"/>',
        extra='<w:next w:val="BodyText"/><w:uiPriority w:val="9"/><w:qFormat/>',
    )


NO_INDENT = '<w:ind w:firstLine="0"/>'
SINGLE = '<w:spacing w:before="0" w:after="0" w:line="240" w:lineRule="auto"/>'

STYLES = f'''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<w:styles {W}>
<w:docDefaults>
  <w:rPrDefault><w:rPr>{FONT}<w:sz w:val="28"/><w:szCs w:val="28"/><w:lang w:val="ru-RU" w:eastAsia="ru-RU" w:bidi="ar-SA"/></w:rPr></w:rPrDefault>
  <w:pPrDefault><w:pPr><w:spacing w:before="0" w:after="0" w:line="360" w:lineRule="auto"/></w:pPr></w:pPrDefault>
</w:docDefaults>
<w:style w:type="paragraph" w:default="1" w:styleId="Normal"><w:name w:val="Normal"/><w:qFormat/>
  <w:pPr><w:ind w:firstLine="709"/><w:jc w:val="both"/></w:pPr><w:rPr>{FONT}<w:color w:val="000000"/><w:sz w:val="28"/><w:szCs w:val="28"/></w:rPr></w:style>
{pstyle("BodyText", "Body Text")}
{pstyle("FirstParagraph", "First Paragraph", based="BodyText")}
{pstyle("Compact", "Compact", ppr=SINGLE + NO_INDENT + '<w:jc w:val="left"/>', rpr='<w:sz w:val="24"/><w:szCs w:val="24"/>', based="BodyText")}
{pstyle("Title", "Title", ppr='<w:jc w:val="center"/>' + NO_INDENT, rpr='<w:b/><w:sz w:val="32"/>')}
{pstyle("Subtitle", "Subtitle", ppr='<w:jc w:val="center"/>' + NO_INDENT)}
{pstyle("Author", "Author", ppr='<w:jc w:val="center"/>' + NO_INDENT)}
{pstyle("Date", "Date", ppr='<w:jc w:val="center"/>' + NO_INDENT)}
{pstyle("Abstract", "Abstract")}
{pstyle("AbstractTitle", "Abstract Title")}
{pstyle("Bibliography", "Bibliography")}
{heading(1, 32, 0, 240, new_page=True)}
{heading(2, 28, 240, 120)}
{heading(3, 28, 120, 60)}
{pstyle("BlockText", "Block Text", ppr='<w:ind w:left="709" w:firstLine="0"/>')}
{pstyle("FootnoteText", "footnote text", ppr=SINGLE, rpr='<w:sz w:val="20"/>')}
{pstyle("Caption", "caption", ppr='<w:keepNext/>' + NO_INDENT + '<w:spacing w:before="120" w:after="60" w:line="240" w:lineRule="auto"/>')}
{pstyle("TableCaption", "Table Caption", ppr='<w:keepNext/>' + NO_INDENT + '<w:spacing w:before="120" w:after="60" w:line="240" w:lineRule="auto"/>', based="Caption")}
{pstyle("ImageCaption", "Image Caption", ppr='<w:jc w:val="center"/>', based="Caption")}
{pstyle("Figure", "Figure", ppr='<w:jc w:val="center"/>' + NO_INDENT)}
{pstyle("CaptionedFigure", "Captioned Figure", based="Figure")}
{pstyle("DefinitionTerm", "Definition Term", ppr='<w:keepNext/>', rpr='<w:b/>')}
{pstyle("Definition", "Definition")}
{pstyle("TOCHeading", "TOC Heading", based="Heading1")}
{pstyle("Titul", "Титул", ppr='<w:jc w:val="center"/>' + NO_INDENT + '<w:spacing w:before="0" w:after="0" w:line="276" w:lineRule="auto"/>')}
{pstyle("TitulBig", "Титул крупно", ppr='<w:jc w:val="center"/>' + NO_INDENT + '<w:spacing w:before="240" w:after="120" w:line="276" w:lineRule="auto"/>', rpr='<w:b/><w:caps/><w:sz w:val="36"/><w:szCs w:val="36"/>')}
{pstyle("TitulRight", "Титул справа", ppr='<w:ind w:left="4536" w:firstLine="0"/><w:jc w:val="left"/><w:spacing w:before="0" w:after="0" w:line="276" w:lineRule="auto"/>')}
{pstyle("TablePodpis", "Подпись таблицы", ppr='<w:keepNext/>' + NO_INDENT + '<w:jc w:val="left"/><w:spacing w:before="240" w:after="60" w:line="240" w:lineRule="auto"/>')}
{pstyle("Formula", "Формула", ppr='<w:jc w:val="center"/>' + NO_INDENT + '<w:spacing w:before="60" w:after="60"/>')}
{pstyle("Primechanie", "Примечание", ppr=SINGLE + '<w:spacing w:before="60" w:after="120" w:line="240" w:lineRule="auto"/>', rpr='<w:sz w:val="24"/><w:szCs w:val="24"/>')}
<w:style w:type="character" w:default="1" w:styleId="DefaultParagraphFont"><w:name w:val="Default Paragraph Font"/><w:uiPriority w:val="1"/><w:semiHidden/></w:style>
<w:style w:type="character" w:customStyle="1" w:styleId="BodyTextChar"><w:name w:val="Body Text Char"/><w:basedOn w:val="DefaultParagraphFont"/></w:style>
<w:style w:type="character" w:customStyle="1" w:styleId="VerbatimChar"><w:name w:val="Verbatim Char"/><w:basedOn w:val="BodyTextChar"/><w:rPr><w:rFonts w:ascii="Consolas" w:hAnsi="Consolas"/><w:sz w:val="22"/></w:rPr></w:style>
<w:style w:type="character" w:customStyle="1" w:styleId="SectionNumber"><w:name w:val="Section Number"/><w:basedOn w:val="BodyTextChar"/></w:style>
<w:style w:type="character" w:styleId="FootnoteReference"><w:name w:val="footnote reference"/><w:basedOn w:val="BodyTextChar"/><w:rPr><w:vertAlign w:val="superscript"/></w:rPr></w:style>
<w:style w:type="character" w:styleId="Hyperlink"><w:name w:val="Hyperlink"/><w:basedOn w:val="BodyTextChar"/><w:rPr><w:color w:val="000000"/></w:rPr></w:style>
<w:style w:type="table" w:default="1" w:styleId="TableNormal"><w:name w:val="Normal Table"/><w:uiPriority w:val="99"/><w:semiHidden/><w:tblPr><w:tblInd w:w="0" w:type="dxa"/><w:tblCellMar><w:top w:w="0" w:type="dxa"/><w:left w:w="108" w:type="dxa"/><w:bottom w:w="0" w:type="dxa"/><w:right w:w="108" w:type="dxa"/></w:tblCellMar></w:tblPr></w:style>
<w:style w:type="table" w:customStyle="1" w:styleId="Table"><w:name w:val="Table"/><w:basedOn w:val="TableNormal"/>
  <w:tblPr><w:jc w:val="center"/><w:tblBorders>
    <w:top w:val="single" w:sz="4" w:space="0" w:color="000000"/><w:left w:val="single" w:sz="4" w:space="0" w:color="000000"/>
    <w:bottom w:val="single" w:sz="4" w:space="0" w:color="000000"/><w:right w:val="single" w:sz="4" w:space="0" w:color="000000"/>
    <w:insideH w:val="single" w:sz="4" w:space="0" w:color="000000"/><w:insideV w:val="single" w:sz="4" w:space="0" w:color="000000"/>
  </w:tblBorders><w:tblCellMar><w:top w:w="28" w:type="dxa"/><w:left w:w="85" w:type="dxa"/><w:bottom w:w="28" w:type="dxa"/><w:right w:w="85" w:type="dxa"/></w:tblCellMar></w:tblPr>
  <w:tblStylePr w:type="firstRow"><w:rPr><w:b/></w:rPr><w:tcPr><w:vAlign w:val="center"/></w:tcPr></w:tblStylePr>
</w:style>
</w:styles>'''

FOOTER = f'''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<w:ftr {W}><w:p><w:pPr><w:jc w:val="center"/><w:ind w:firstLine="0"/></w:pPr>
<w:r><w:fldChar w:fldCharType="begin"/></w:r><w:r><w:instrText xml:space="preserve"> PAGE </w:instrText></w:r>
<w:r><w:fldChar w:fldCharType="separate"/></w:r><w:r><w:t>2</w:t></w:r><w:r><w:fldChar w:fldCharType="end"/></w:r></w:p></w:ftr>'''

SECT = ('<w:sectPr><w:footerReference w:type="default" r:id="rIdFtr1"/>'
        '<w:footnotePr><w:numRestart w:val="eachSect"/></w:footnotePr>'
        '<w:pgSz w:w="11906" w:h="16838"/>'
        '<w:pgMar w:top="1134" w:right="850" w:bottom="1134" w:left="1701" w:header="709" w:footer="567" w:gutter="0"/>'
        '<w:titlePg/></w:sectPr>')


def main():
    base = subprocess.run(["pandoc", "--print-default-data-file", "reference.docx"],
                          check=True, capture_output=True).stdout
    zin = zipfile.ZipFile(io.BytesIO(base))
    out = zipfile.ZipFile("reference.docx", "w", zipfile.ZIP_DEFLATED)
    for item in zin.infolist():
        data = zin.read(item.filename)
        name = item.filename
        if name == "word/styles.xml":
            data = STYLES.encode()
        elif name == "word/document.xml":
            s = data.decode()
            if 'xmlns:r=' not in s:
                s = s.replace("<w:document ", '<w:document xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships" ', 1)
            s = re.sub(r"<w:sectPr>.*?</w:sectPr>", SECT, s, flags=re.S)
            data = s.encode()
        elif name == "word/_rels/document.xml.rels":
            data = data.replace(b"</Relationships>",
                                b'<Relationship Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/footer" '
                                b'Id="rIdFtr1" Target="footer1.xml"/></Relationships>')
        elif name == "[Content_Types].xml":
            data = data.replace(b"</Types>",
                                b'<Override PartName="/word/footer1.xml" '
                                b'ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.footer+xml"/></Types>')
        info = zipfile.ZipInfo(name, date_time=(1980, 1, 1, 0, 0, 0))
        info.compress_type = zipfile.ZIP_DEFLATED
        out.writestr(info, data)
    info = zipfile.ZipInfo("word/footer1.xml", date_time=(1980, 1, 1, 0, 0, 0))
    info.compress_type = zipfile.ZIP_DEFLATED
    out.writestr(info, FOOTER.encode())
    out.close()


if __name__ == "__main__":
    main()
