const fs = require("fs");
const path = require("path");
const {
  Document, Packer, Paragraph, TextRun, Table, TableRow, TableCell,
  WidthType, AlignmentType, ShadingType, BorderStyle, VerticalAlign, TableLayoutType,
} = require("docx");

// 公文常用格式常量
const FONT_FAINGSONG = "仿宋_GB2312";
const FONT_HEI = "黑体";
const FONT_FANGSONG_FALLBACK = "仿宋";

function bodyText(text, opts = {}) {
  return new TextRun({
    text,
    font: { ascii: "Times New Roman", eastAsia: opts.font || FONT_FAINGSONG, hAnsi: "Times New Roman" },
    size: opts.size || 32, // 16pt
    bold: !!opts.bold,
  });
}

function p(text, opts = {}) {
  return new Paragraph({
    children: [bodyText(text, opts)],
    alignment: opts.align || AlignmentType.JUSTIFIED,
    spacing: { line: 360 }, // 1.5倍行距
    indent: opts.indent ? { firstLine: 640 } : undefined, // 首行缩进2字符
  });
}

// 标题行
const title = new Paragraph({
  children: [
    new TextRun({
      text: "关于五冶集团有限公司安岳县2025年高标准农田建设",
      font: { ascii: "Times New Roman", eastAsia: FONT_HEI, hAnsi: "Times New Roman" },
      size: 44, // 22pt
      bold: true,
    }),
  ],
  alignment: AlignmentType.CENTER,
  spacing: { line: 360, after: 0 },
});

const title2 = new Paragraph({
  children: [
    new TextRun({
      text: "项目（地方专项债券）农民工工资发放情况的说明",
      font: { ascii: "Times New Roman", eastAsia: FONT_HEI, hAnsi: "Times New Roman" },
      size: 44,
      bold: true,
    }),
  ],
  alignment: AlignmentType.CENTER,
  spacing: { line: 360, after: 240 },
});

const blank = new Paragraph({ children: [] });

// 正文
const para1 = p("为如实反映安岳县2025年高标准农田建设项目（地方专项债券）农民工工资支付情况，五冶集团有限公司对2025年4月、5月工资发放情况进行了梳理核对，现将有关情况说明如下：", { indent: true });
const para2 = p("2025年4月、5月农民工工资已按时足额发放。经与各班组逐一核对，截至目前尚有部分班组工资未结清，明细如下：", { indent: true });

// 表格
const tableHeader = (text) =>
  new TextRun({
    text,
    font: { ascii: "Times New Roman", eastAsia: FONT_HEI, hAnsi: "Times New Roman" },
    size: 28,
    bold: true,
  });
const tableBodyText = (text) =>
  new TextRun({
    text,
    font: { ascii: "Times New Roman", eastAsia: FONT_FAINGSONG, hAnsi: "Times New Roman" },
    size: 28,
  });

const cell = (children, opts = {}) =>
  new TableCell({
    children: [
      new Paragraph({
        children,
        alignment: opts.align || AlignmentType.CENTER,
        spacing: { line: 320 },
      }),
    ],
    width: { size: opts.width || 50, type: WidthType.PERCENTAGE },
    verticalAlign: VerticalAlign.CENTER,
    shading: opts.shading ? { type: ShadingType.CLEAR, fill: opts.fill || "F2F2F2" } : undefined,
  });

const tbl = new Table({
  width: { size: 100, type: WidthType.PERCENTAGE },
  layout: TableLayoutType.FIXED,
  columnWidths: [5200, 5200],
  rows: [
    new TableRow({
      tableHeader: true,
      children: [
        cell([tableHeader("班组")], { width: 50, align: AlignmentType.CENTER, shading: true, fill: "D9D9D9" }),
        cell([tableHeader("剩余未付金额（元）")], { width: 50, align: AlignmentType.CENTER, shading: true, fill: "D9D9D9" }),
      ],
    }),
    new TableRow({
      children: [
        cell([tableBodyText("周成习班组")], { width: 50 }),
        cell([tableBodyText("11986")], { width: 50 }),
      ],
    }),
    new TableRow({
      children: [
        cell([tableBodyText("何永兵班组")], { width: 50 }),
        cell([tableBodyText("21429")], { width: 50 }),
      ],
    }),
    new TableRow({
      children: [
        cell([tableBodyText("彭松林")], { width: 50 }),
        cell([tableBodyText("10198")], { width: 50 }),
      ],
    }),
    new TableRow({
      children: [
        cell([tableHeader("合计")], { width: 50, align: AlignmentType.CENTER, shading: true, fill: "D9D9D9" }),
        cell([tableHeader("43613")], { width: 50, align: AlignmentType.CENTER, shading: true, fill: "D9D9D9" }),
      ],
    }),
  ],
});

const para3 = p("下一步，五冶集团有限公司将加快剩余工资结算进度，确保农民工工资足额支付到位，切实保障农民工合法权益。", { indent: true });
const para4 = p("特此说明。", { indent: true });

// 落款（右对齐）
const signer = new Paragraph({
  children: [bodyText("说明人：______________")],
  alignment: AlignmentType.RIGHT,
  spacing: { line: 360 },
});
const date = new Paragraph({
  children: [bodyText("日期：______________")],
  alignment: AlignmentType.RIGHT,
  spacing: { line: 360 },
});

const doc = new Document({
  creator: "Amer-CN",
  title: "关于五冶集团有限公司安岳县2025年高标准农田建设项目（地方专项债券）农民工工资发放情况的说明",
  styles: {
    default: {
      document: { run: { font: { eastAsia: FONT_FAINGSONG } } },
    },
  },
  sections: [
    {
      properties: {
        page: {
          margin: { top: 1440, bottom: 1440, left: 1440, right: 1440 },
        },
      },
      children: [title, title2, blank, para1, para2, tbl, blank, para3, para4, blank, signer, date],
    },
  ],
});

Packer.toBuffer(doc).then((buf) => {
  const out = path.join(__dirname, "工资发放情况说明.docx");
  fs.writeFileSync(out, buf);
  console.log("written:", out, buf.length, "bytes");
});
