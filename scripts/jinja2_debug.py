import os
from jinja2 import Environment, FileSystemLoader

base_dir = os.path.dirname(os.path.abspath(__file__))
template_dir = os.path.join(base_dir, "templates")
env = Environment(loader=FileSystemLoader(template_dir))

if __name__ == "__main__":
    # template = env.get_template("hello.html")
    # output = template.render(name="nonocast")
    # print(output)

    # 加载模板
    template = env.get_template("checklist.html")

    # 模拟数据
    checklist_data = {
        "title": "我的英语学习清单",
        "checklist": [
            {
                "name": "词汇",
                "tasks": [
                    {"text": "背完B1词汇表", "done": True},
                    {"text": "掌握100个动词短语", "done": False},
                ]
            },
            {
                "name": "听力",
                "tasks": [
                    {"text": "每天听 vlog 10 分钟", "done": True},
                    {"text": "练习 shadowing", "done": False},
                ]
            },
            {
                "name": "口语",
                "tasks": [
                    
                    {"text": "完成 ELSA 每日练习", "done": True},
                    {"text": "模拟旅游情境对话", "done": False},
                ]
            },
        ]
    }

    # 渲染
    output_html = template.render(**checklist_data)

    # 输出到文件
    output_dir = os.path.join(base_dir, "output")
    os.makedirs(output_dir, exist_ok=True)
    with open(os.path.join(output_dir, "checklist.html"), "w", encoding="utf-8") as f:
        f.write(output_html)

    print("✅ 渲染完成：output/checklist.html")