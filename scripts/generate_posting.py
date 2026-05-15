#!/usr/bin/env python3
"""
小红书笔记文案生成脚本
自动根据渲染的 Markdown 内容生成标题建议、描述文案和话题标签
"""

import os
import sys
import re
from pathlib import Path


def extract_content_from_markdown(markdown_path):
    """从 Markdown 文件中提取关键内容"""
    with open(markdown_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # 提取 YAML 元数据
    yaml_match = re.search(r'^---\s*\n(.*?)\n---', content, re.DOTALL)
    yaml_content = {}
    if yaml_match:
        yaml_text = yaml_match.group(1)
        for line in yaml_text.split('\n'):
            if ':' in line:
                key, value = line.split(':', 1)
                key = key.strip()
                value = value.strip().strip('"\'')
                yaml_content[key] = value

    # 提取所有二级标题和内容
    headings = re.findall(r'^#+\s+(.*?)$', content, re.MULTILINE)

    # 提取第一个段落（非标题内容）
    first_content = ""
    # 跳过 YAML 部分
    content_after_yaml = content
    if yaml_match:
        content_after_yaml = content[yaml_match.end():]

    # 找到第一个非标题段落
    lines = content_after_yaml.split('\n')
    for line in lines:
        line = line.strip()
        if line and not line.startswith('#') and not line.startswith('---'):
            first_content = line
            if len(first_content) > 100:
                first_content = first_content[:100] + "..."
            break

    return {
        'yaml': yaml_content,
        'headings': headings,
        'first_content': first_content,
        'card_count': len([h for h in headings if not h.startswith('---')]) - 1  # 减去封面标题
    }


def generate_titles(yaml_content, card_count, topic):
    """生成标题建议"""
    title = yaml_content.get('title', '')
    subtitle = yaml_content.get('subtitle', '')
    emoji = yaml_content.get('emoji', '')

    titles = []

    # 方案1：原标题 + 感叹号 + emoji
    if title:
        base_title = title.replace('指南', '').replace('教程', '').replace('入门', '')
        titles.append(f"{base_title}{emoji}")

    # 方案2：疑问句/惊叹句
    if 'Git' in title or 'git' in title.lower():
        titles.append(f"Git 不用背命令？{title.split()[0]}来救你！")

    # 方案3：数字吸引
    if card_count > 0:
        titles.append(f"{card_count} 张图搞定{title}！")

    # 方案4：行动号召
    if subtitle:
        short_sub = subtitle[:10] if len(subtitle) > 10 else subtitle
        titles.append(f"告别命令行，用{short_sub}玩转{title.split()[0]}！")

    # 方案5：简单直接
    titles.append(f"程序员必备：{title}")

    # 去重并确保不超过20字
    unique_titles = []
    seen = set()
    for t in titles:
        if t and t not in seen and len(t) <= 20:
            unique_titles.append(t)
            seen.add(t)

    return unique_titles[:5]  # 最多5个


def generate_description(yaml_content, first_content, card_count):
    """生成描述文案"""
    title = yaml_content.get('title', '')
    subtitle = yaml_content.get('subtitle', '')

    description = f"{subtitle}，{first_content}\n\n"

    # 添加亮点
    if card_count > 0:
        description += f"📝 {card_count} 张卡片涵盖核心内容\n"

    description += "💻 图文结合，一看就懂\n"
    description += "🚀 提升效率，告别繁琐\n\n"

    description += "让操作也能成为一种享受！" + yaml_content.get('emoji', '')

    return description


def generate_hashtags(yaml_content, headings):
    """生成话题标签"""
    title = yaml_content.get('title', '').lower()
    subtitle = yaml_content.get('subtitle', '').lower()

    core_tags = []
    tech_tags = []
    style_tags = []

    # 根据内容关键词生成标签
    keywords = {
        'git': ['Git可视化', '版本控制', '代码管理'],
        '终端': ['终端工具', '命令行', 'Shell'],
        '效率': ['开发效率', '效率提升', '工作效率'],
        '程序员': ['程序员必备', '开发工具', '编程工具'],
        '教程': ['技术教程', '入门指南', '学习笔记'],
    }

    # 核心标签（基于标题）
    for key, tags in keywords.items():
        if key in title or key in subtitle:
            core_tags.extend(tags[:2])

    # 如果没有匹配到，使用默认核心标签
    if not core_tags:
        core_tags = ['技术分享', '工具推荐', '效率工具']

    # 技术相关标签
    tech_keywords = ['python', 'javascript', 'java', 'go', 'rust', 'react', 'vue', 'docker', 'kubernetes']
    for kw in tech_keywords:
        if kw in title or any(kw in h.lower() for h in headings):
            tech_tags.append(f'#{kw.capitalize()}')

    # 风格标签
    style_tags = ['#技术分享', '#工具推荐', '#效率工具', '#开发神器', '#程序员好物', '#学习笔记']

    # 合并所有标签，去重
    all_tags = list(dict.fromkeys(core_tags + tech_tags + style_tags))

    # 格式化为 # 标签
    hashtags = []
    for tag in all_tags:
        if not tag.startswith('#'):
            hashtags.append(f'#{tag}')
        else:
            hashtags.append(tag)

    return hashtags[:15]  # 最多15个标签


def main():
    if len(sys.argv) < 2:
        print("用法: python generate_posting.py <markdown文件>")
        sys.exit(1)

    markdown_path = Path(sys.argv[1])
    if not markdown_path.exists():
        print(f"错误: 文件不存在 {markdown_path}")
        sys.exit(1)

    # 提取内容
    content_info = extract_content_from_markdown(markdown_path)

    # 生成文案
    titles = generate_titles(content_info['yaml'], content_info['card_count'], "技术")
    description = generate_description(content_info['yaml'], content_info['first_content'], content_info['card_count'])
    hashtags = generate_hashtags(content_info['yaml'], content_info['headings'])

    # 生成输出文件名
    output_path = markdown_path.parent / f"{markdown_path.stem}_posting.txt"

    # 写入文件
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write("=" * 60 + "\n")
        f.write("小红书笔记发布文案\n")
        f.write("=" * 60 + "\n\n")

        f.write("📌 标题建议（选一，不超过20字）：\n")
        for i, title in enumerate(titles, 1):
            f.write(f"{i}. {title}\n")
        f.write("\n")

        f.write("📝 描述文案：\n")
        f.write(description)
        f.write("\n\n")

        f.write("🏷️ 话题标签：\n")
        f.write(" ".join(hashtags))
        f.write("\n\n")

        f.write("=" * 60 + "\n")
        f.write("使用发布命令：\n")
        f.write(f"python scripts/publish_xhs.py --title \"{titles[0]}\" \\\n")
        f.write(f"  --desc \"{description[:50]}...\" \\\n")
        f.write("  --images cover.png card_*.png\n")
        f.write("=" * 60 + "\n")

    print(f"✅ 已生成发布文案: {output_path}")

    # 控制台输出预览
    print("\n" + "=" * 60)
    print("文案预览：")
    print("=" * 60)
    print("\n标题建议：")
    for i, title in enumerate(titles[:3], 1):
        print(f"  {i}. {title}")

    print(f"\n描述（前100字）：")
    print(f"  {description[:100]}...")

    print(f"\n标签（前10个）：")
    print(f"  {' '.join(hashtags[:10])}")
    print("=" * 60)


if __name__ == "__main__":
    main()