#!/usr/bin/env node
/**
 * render_docx.js — 超级公文写作 Skill 排版执行层
 *
 * 输入结构化 JSON，输出 GB/T 9704-2012 格式的 .docx：
 *   标题：方正小标宋简体 二号（缺字体时回退 黑体）
 *   一级标题：黑体 三号 不加粗
 *   二级标题：楷体_GB2312 三号 不加粗
 *   正文：仿宋_GB2312 三号
 *   行距：固定值 28 磅；页边距 上3.7/下3.5/左2.8/右2.6 cm
 *   落款：右对齐（说明人/日期）
 *
 * 用法：
 *   node render_docx.js input.json            # input.json 见下方 INPUT_SCHEMA
 *   node render_docx.js --demo               # 内置样例，生成 demo.docx
 *
 * INPUT_SCHEMA（字段均可省略，至少给 title + body）：
 * {
 *   "title": "关于XX工作的通知",
 *   "sub_title": "——补充说明",           // 可选，标题下副行
 *   "body": [
 *     {"level": "h1", "text": "一、总体要求"},
 *     {"level": "h2", "text": "（一）指导思想"},
 *     {"level": "para", "text": "正文段落……"},
 *     {"level": "para", "text": "特此通知。"}
 *   ],
 *   "signee": "XX单位",
 *   "date": "2026年9月2日",
 *   "out": "output.docx"
 * }
 *
 * 依赖：docx (npm)。若报 Cannot find module 'docx'：
 *   cd <skill目录>/scripts && npm install docx
 * 或全局：npm install -g docx && export NODE_PATH=$(npm root -g)
 */
"use strict";

const fs = require("fs");
const path = require("path");

const CM = 567; // 1cm ≈ 567 twips (DXA)

const F = {
  titleFont: { ascii: "FZXiaoBiaoSong-B05S", eastAsia: "FZXiaoBiaoSong-B05S", hAnsi: "FZXiaoBiaoSong-B05S" },
  titleFontFallback: { ascii: "黑体", eastAsia: "黑体", hAnsi: "黑体" },
  h1: { ascii: "黑体", eastAsia: "黑体", hAnsi: "黑体" },
  h2: { ascii: "楷体_GB2312", eastAsia: "楷体_GB2312", hAnsi: "楷体_GB2312" },
  body: { ascii: "仿宋_GB2312", eastAsia: "仿宋_GB2312", hAnsi: "仿宋_GB2312" },
};
const SIZE = { title: 44, section: 32 }; // docx half-points: 22pt=44, 16pt(三号)=32

function tryDocx() {
  try {
    return require("docx");
  } catch (e) {
    const local = path.join(__dirname, "node_modules", "docx");
    try {
      return require(local);
    } catch (e2) {
      console.error("[依赖缺失] 需要 npm 包 docx。安装方法：");
      console.error("  cd " + __dirname + " && npm install docx");
      process.exit(2);
    }
  }
}

function build(docx, input) {
  const { Document, Packer, Paragraph, TextRun, AlignmentType } = docx;

  const titleFont = input.titleFontFallback ? F.titleFontFallback : F.titleFont;
  const children = [];

  children.push(new Paragraph({
    children: [new TextRun({ text: input.title, font: titleFont, size: SIZE.title, bold: true })],
    alignment: AlignmentType.CENTER,
    spacing: { line: 560, after: 240, lineRule: "exact" }, // 28pt = 560 twips
  }));
  if (input.sub_title) {
    children.push(new Paragraph({
      children: [new TextRun({ text: input.sub_title, font: titleFont, size: SIZE.section, bold: true })],
      alignment: AlignmentType.CENTER,
      spacing: { line: 560, after: 240, lineRule: "exact" },
    }));
  }

  for (const blk of input.body || []) {
    if (blk.level === "h1") {
      children.push(new Paragraph({
        children: [new TextRun({ text: blk.text, font: F.h1, size: SIZE.section })],
        spacing: { line: 560, before: 120, lineRule: "exact" },
        indent: { firstLine: 2 * 320 },
      }));
    } else if (blk.level === "h2") {
      children.push(new Paragraph({
        children: [new TextRun({ text: blk.text, font: F.h2, size: SIZE.section })],
        spacing: { line: 560, before: 60, lineRule: "exact" },
        indent: { firstLine: 2 * 320 },
      }));
    } else {
      children.push(new Paragraph({
        children: [new TextRun({ text: blk.text, font: F.body, size: SIZE.section })],
        spacing: { line: 560, lineRule: "exact" },
        indent: { firstLine: 2 * 320 },
        alignment: AlignmentType.JUSTIFIED,
      }));
    }
  }

  if (input.signee) {
    children.push(new Paragraph({
      children: [new TextRun({ text: input.signee, font: F.body, size: SIZE.section })],
      alignment: AlignmentType.RIGHT,
      spacing: { line: 560, before: 480, lineRule: "exact" },
    }));
  }
  if (input.date) {
    children.push(new Paragraph({
      children: [new TextRun({ text: input.date, font: F.body, size: SIZE.section })],
      alignment: AlignmentType.RIGHT,
      spacing: { line: 560, lineRule: "exact" },
    }));
  }

  return new Document({
    creator: "super-official-writer v0.3",
    title: input.title,
    sections: [{
      properties: {
        page: {
          margin: { top: 3.7 * CM, bottom: 3.5 * CM, left: 2.8 * CM, right: 2.6 * CM },
        },
      },
      children,
    }],
  });
}

const DEMO = {
  title: "关于开展2026年度公文写作规范化培训的通知",
  body: [
    { level: "para", text: "为提升机关公文写作规范化水平，经研究，决定开展2026年度公文写作培训。现将有关事项通知如下。" },
    { level: "h1", text: "一、培训内容" },
    { level: "h2", text: "（一）基础规范" },
    { level: "para", text: "重点学习《党政机关公文处理工作条例》和GB/T 9704-2012格式国家标准，掌握法定文种使用与版面要素编排。" },
    { level: "h2", text: "（二）实战方法" },
    { level: "para", text: "围绕标题提炼、结构搭建、语言润色三个环节开展案例教学，结合本单位近期文稿开展现场修改。" },
    { level: "h1", text: "二、培训安排" },
    { level: "para", text: "培训定于2026年9月10日（星期四）下午2:30在三楼会议室举行，请各部门安排1名文稿起草人员参加。" },
    { level: "para", text: "特此通知。" },
  ],
  signee: "××单位办公室",
  date: "2026年9月2日",
  out: path.join(__dirname, "..", "word", "demo.docx"),
};

function main() {
  const docx = tryDocx();
  let input;
  const arg = process.argv[2];
  if (arg === "--demo") {
    input = DEMO;
  } else if (arg) {
    input = JSON.parse(fs.readFileSync(arg, "utf-8"));
  } else {
    input = JSON.parse(fs.readFileSync(0, "utf-8")); // stdin
  }
  const outPath = input.out || (arg && arg.replace(/\.json$/i, ".docx")) || "output.docx";
  const Packer = docx.Packer;
  Packer.toBuffer(build(docx, input)).then(buf => {
    const p = path.isAbsolute(outPath) ? outPath : path.join(process.cwd(), outPath);
    fs.mkdirSync(path.dirname(p), { recursive: true });
    fs.writeFileSync(p, buf);
    console.log("[ok] written:", p, buf.length, "bytes");
  }).catch(err => { console.error(err); process.exit(1); });
}

main();
