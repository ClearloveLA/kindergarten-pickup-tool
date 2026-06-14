import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import datetime
import json
import os
import pyttsx3
import threading
import time
import gc

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_FILE = os.path.join(BASE_DIR, "pickup_data.json")

class KindergartenPickupApp:
    def __init__(self, root):
        self.root = root
        self.root.title("高新区崇仁路幼儿园离园管理系统")
        self.root.geometry("1000x750")
        self.root.configure(bg='#f0f8ff')

        # 广播状态控制
        self.is_broadcasting = False
        self.broadcast_thread = None
        self.lock = threading.Lock()

        # 预设数据
        self.classes = ["小班", "中班", "大班"]
        self.teachers = ["张老师", "李老师", "王老师", "刘老师", "陈老师"]
        self.securities = ["保安张", "保安李", "保安王"]

        self.setup_ui()

    def setup_voice_properties(self):
        voices = self.engine.getProperty('voices')
        if voices:
            for voice in voices:
                if 'zh' in voice.id.lower() or 'chinese' in voice.name.lower():
                    self.engine.setProperty('voice', voice.id)
                    break
        self.engine.setProperty('rate', 200)
        self.engine.setProperty('volume', 0.9)

    def setup_ui(self):
        # 标题
        title_label = tk.Label(self.root, text="高新区崇仁路幼儿园离园管理系统",
                           font=("Arial", 20, "bold"),
                           bg='#f0f8ff', fg='#2c3e50')
        title_label.pack(pady=15)

        # 主框架
        main_frame = tk.Frame(self.root, bg='#f0f8ff')
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)

        # 左侧输入区域
        input_frame = tk.LabelFrame(main_frame, text="接送登记",
                                font=("Arial", 12, "bold"),
                                bg='#f0f8ff', fg='#34495e')
        input_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10)

        # 孩子姓名
        tk.Label(input_frame, text="孩子姓名:", font=("Arial", 10),
                 bg='#f0f8ff').grid(row=0, column=0, sticky='w', padx=10, pady=10)
        self.child_name_entry = tk.Entry(input_frame, font=("Arial", 10), width=20)
        self.child_name_entry.grid(row=0, column=1, padx=10, pady=10)

        # 班级选择
        tk.Label(input_frame, text="选择班级:", font=("Arial", 10),
                 bg='#f0f8ff').grid(row=1, column=0, sticky='w', padx=10, pady=10)
        self.class_var = tk.StringVar()
        self.class_combobox = ttk.Combobox(input_frame, textvariable=self.class_var,
                                       values=self.classes, state="readonly", width=18)
        self.class_combobox.grid(row=1, column=1, padx=10, pady=11)
        self.class_combobox.set(self.classes[0])

        # 新增班级按钮
        add_class_btn = tk.Button(input_frame, text="新增班级",
                                  command=self.add_new_class,
                                  bg='#3498db', fg='white', font=("Arial", 8))
        add_class_btn.grid(row=1, column=2, padx=5, pady=10)

        # 家长姓名
        tk.Label(input_frame, text="家长姓名:", font=("Arial", 10),
                 bg='#f0f8ff').grid(row=2, column=0, sticky='w', padx=10, pady=10)
        self.parent_name_entry = tk.Entry(input_frame, font=("Arial", 10), width=20)
        self.parent_name_entry.grid(row=2, column=1, padx=10, pady=10)

        # 老师选择
        tk.Label(input_frame, text="选择老师:", font=("Arial", 10),
                 bg='#f0f8ff').grid(row=3, column=0, sticky='w', padx=10, pady=10)
        self.teacher_var = tk.StringVar()
        self.teacher_combobox = ttk.Combobox(input_frame, textvariable=self.teacher_var,
                                         values=self.teachers, state="readonly", width=18)
        self.teacher_combobox.grid(row=3, column=1, padx=10, pady=10)
        self.teacher_combobox.set(self.teachers[0])

        # 新增老师按钮
        add_teacher_btn = tk.Button(input_frame, text="新增老师",
                                    command=self.add_new_teacher,
                                    bg='#3498db', fg='white', font=("Arial", 8))
        add_teacher_btn.grid(row=3, column=2, padx=5, pady=10)

        # 安全员选择
        tk.Label(input_frame, text="选择安全员:", font=("Arial", 10),
                 bg='#f0f8ff').grid(row=4, column=0, sticky='w', padx=10, pady=10)
        self.security_var = tk.StringVar()
        self.security_combobox = ttk.Combobox(input_frame, textvariable=self.security_var,
                                          values=self.securities, state="readonly", width=18)
        self.security_combobox.grid(row=4, column=1, padx=10, pady=10)
        self.security_combobox.set(self.securities[0])

        # 新增安全员按钮
        add_security_btn = tk.Button(input_frame, text="新增安全员",
                                     command=self.add_new_security,
                                     bg='#3498db', fg='white', font=("Arial", 8))
        add_security_btn.grid(row=4, column=2, padx=5, pady=10)

        # 按钮区域
        button_frame = tk.Frame(input_frame, bg='#f0f8ff')
        button_frame.grid(row=5, column=0, columnspan=3, pady=20)

        # 登记按钮
        register_btn = tk.Button(button_frame, text="登记接送",
                                 command=self.register_pickup,
                                 bg='#27ae60', fg='white', font=("Arial", 12, "bold"),
                                 width=15, height=2)
        register_btn.pack(side=tk.LEFT, padx=10)

        # 广播按钮
        self.broadcast_btn = tk.Button(button_frame, text="广播通知",
                                       command=self.toggle_broadcast,
                                       bg='#e74c3c', fg='white', font=("Arial", 12, "bold"),
                                       width=15, height=2)
        self.broadcast_btn.pack(side=tk.LEFT, padx=10)

        # 右侧显示区域
        display_frame = tk.LabelFrame(main_frame, text="接送记录",
                                      font=("Arial", 12, "bold"),
                                      bg='#f0f8ff', fg='#34495e')
        display_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=10)

        # 创建Treeview显示接送记录
        columns = ("孩子姓名", "班级", "家长姓名", "老师姓名", "安全员", "接送时间")
        self.tree = ttk.Treeview(display_frame, columns=columns, show='headings', height=15)

        # 设置列标题
        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=90, anchor='center')

        # 添加滚动条
        scrollbar = ttk.Scrollbar(display_frame, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscroll=scrollbar.set)

        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=5)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # 绑定双击事件
        self.tree.bind("<Double-1>", self.on_tree_double_click)

        # 底部按钮
        bottom_frame = tk.Frame(self.root, bg='#f0f8ff')
        bottom_frame.pack(fill=tk.X, padx=20, pady=10)

        refresh_btn = tk.Button(bottom_frame, text="刷新记录",
                                command=self.load_pickup_data,
                                bg='#9b59b6', fg='white', font=("Arial", 10))
        refresh_btn.pack(side=tk.LEFT, padx=5)

        clear_btn = tk.Button(bottom_frame, text="清空记录",
                              command=self.clear_all_data,
                              bg='#e67e22', fg='white', font=("Arial", 10))
        clear_btn.pack(side=tk.LEFT, padx=5)

        # 开发人员信息
        dev_frame = tk.Frame(self.root, bg='#e3f2fd', relief='ridge', bd=2)
        dev_frame.pack(side=tk.BOTTOM, fill=tk.X, padx=20, pady=5)
        dev_label = tk.Label(dev_frame, text="开发人员：ClearloveLA  GitHub：github.com/ClearloveLA",
                             font=("Arial", 10), bg='#e3f2fd', fg='#555555')
        dev_label.pack(pady=5)

        # 加载数据
        self.load_pickup_data()

    def load_data(self):
        if not os.path.exists(DATA_FILE):
            return []
        with open(DATA_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)

    def save_data(self, data):
        with open(DATA_FILE, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=4)

    def setup_voice_properties_for_engine(self, engine):
        """为语音引擎设置语音属性"""
        try:
            voices = engine.getProperty('voices')
            if voices:
                for voice in voices:
                    if 'zh' in voice.id.lower() or 'chinese' in voice.name.lower():
                        engine.setProperty('voice', voice.id)
                        break
            engine.setProperty('rate', 200)
            engine.setProperty('volume', 0.9)
        except Exception as e:
            print(f"设置语音属性失败: {e}")

    def speak_once(self, text):
        """单次语音播报，确保资源正确清理"""
        engine = None
        try:
            # 创建新的引擎实例
            engine = pyttsx3.init()
            self.setup_voice_properties_for_engine(engine)
            
            # 播报
            engine.say(text)
            engine.runAndWait()
            
            # 等待播报完成
            time.sleep(0.5)
            
        except Exception as e:
            print(f"单次语音播报失败: {e}")
        finally:
            # 确保引擎被完全清理
            if engine is not None:
                try:
                    engine.stop()
                except:
                    pass
                try:
                    del engine
                except:
                    pass
            # 强制垃圾回收
            gc.collect()

    def broadcast_announcement(self, announcement):
        """执行3次广播播报，每次间隔2秒"""
        try:
            for i in range(3):
                if not self.is_broadcasting:
                    break
                
                # 使用改进的单次播报方法
                self.speak_once(announcement)
                
                # 最后一次播报后不需要等待
                if i < 2 and self.is_broadcasting:
                    time.sleep(2)
                    
        except Exception as e:
            print(f"语音播报失败: {e}")
        finally:
            # 确保状态重置
            if self.is_broadcasting:
                self.root.after(0, lambda: self.broadcast_btn.config(text="广播通知", bg='#e74c3c'))
                self.is_broadcasting = False

    def toggle_broadcast(self):
        """切换广播状态"""
        child_name = self.child_name_entry.get().strip()
        class_name = self.class_var.get()

        if not child_name:
            messagebox.showwarning("警告", "请输入孩子姓名！")
            return

        if not class_name:
            messagebox.showwarning("警告", "请选择班级！")
            return

        announcement = f"请 {class_name} 的 {child_name} 到校门口等待家长接送"

        if not self.is_broadcasting:
            # 开始广播
            self.is_broadcasting = True
            self.broadcast_btn.config(text="停止广播", bg='#e67e22')
            # 在新线程中执行广播
            self.broadcast_thread = threading.Thread(
                target=self.broadcast_announcement, 
                args=(announcement,)
            )
            self.broadcast_thread.daemon = True
            self.broadcast_thread.start()
        else:
            # 停止广播
            self.is_broadcasting = False
            self.broadcast_btn.config(text="广播通知", bg='#e74c3c')

    def register_pickup(self):
        child_name = self.child_name_entry.get().strip()
        class_name = self.class_var.get()
        parent_name = self.parent_name_entry.get().strip()
        teacher_name = self.teacher_var.get()
        security_name = self.security_var.get()

        if not child_name:
            messagebox.showwarning("警告", "请输入孩子姓名！")
            return

        if not class_name:
            messagebox.showwarning("警告", "请选择班级！")
            return

        if not parent_name:
            messagebox.showwarning("警告", "请输入家长姓名！")
            return

        if not teacher_name:
            messagebox.showwarning("警告", "请选择老师！")
            return

        if not security_name:
            messagebox.showwarning("警告", "请选择安全员！")
            return

        # 记录接送信息
        data = self.load_data()
        record = {
            "child_name": child_name,
            "class_name": class_name,
            "parent_name": parent_name,
            "teacher_name": teacher_name,
            "security_name": security_name,
            "pickup_time": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        data.append(record)
        self.save_data(data)

        # 更新显示
        self.load_pickup_data()

        # 清空输入
        self.child_name_entry.delete(0, tk.END)
        self.parent_name_entry.delete(0, tk.END)

        messagebox.showinfo("成功", "接送信息已记录！")

    def load_pickup_data(self):
        # 清空现有数据
        for item in self.tree.get_children():
            self.tree.delete(item)

        # 加载数据
        data = self.load_data()
        for record in data:
            self.tree.insert("", tk.END, values=(
                record["child_name"],
                record.get("class_name", "未指定"),
                record["parent_name"],
                record["teacher_name"],
                record["security_name"],
                record["pickup_time"]
            ))

    def clear_all_data(self):
        if messagebox.askyesno("确认", "确定要清空所有接送记录吗？"):
            self.save_data([])
            self.load_pickup_data()
            messagebox.showinfo("成功", "所有记录已清空！")

    def add_new_class(self):
        new_class = simpledialog.askstring("新增班级", "请输入新班级名称:")
        if new_class and new_class.strip():
            if new_class not in self.classes:
                self.classes.append(new_class.strip())
                self.class_combobox['values'] = self.classes
            self.class_var.set(new_class.strip())

    def add_new_teacher(self):
        new_teacher = simpledialog.askstring("新增老师", "请输入新老师姓名:")
        if new_teacher and new_teacher.strip():
            if new_teacher not in self.teachers:
                self.teachers.append(new_teacher.strip())
                self.teacher_combobox['values'] = self.teachers
            self.teacher_combobox.set(new_teacher.strip())

    def add_new_security(self):
        new_security = simpledialog.askstring("新增安全员", "请输入新安全员姓名:")
        if new_security and new_security.strip():
            if new_security not in self.securities:
                self.securities.append(new_security.strip())
                self.security_combobox['values'] = self.securities
            self.security_var.set(new_security.strip())

    def on_tree_double_click(self, event):
        """双击记录项执行语音播报"""
        selected_item = self.tree.selection()
        if selected_item:
            item = self.tree.item(selected_item)
            values = item['values']
            if values and len(values) >= 2:
                announcement = f"请 {values[1]} 的 {values[0]} 到校门口等待家长接送"
                # 在新线程中执行播报
                broadcast_thread = threading.Thread(
                    target=self.repeat_broadcast, 
                    args=(announcement,)
                )
                broadcast_thread.daemon = True
                broadcast_thread.start()

    def repeat_broadcast(self, announcement):
        """重复播报3次，每次间隔2秒"""
        try:
            for i in range(3):
                # 使用改进的单次播报方法
                self.speak_once(announcement)
                
                # 最后一次播报后不需要等待
                if i < 2:
                    time.sleep(2)
                    
        except Exception as e:
            print(f"语音播报失败: {e}")

def main():
    root = tk.Tk()
    app = KindergartenPickupApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()

