import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
import threading
from tkcalendar import DateEntry
import time

class EnhancedScheduleTrackerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("SCHEDULE TRACKING APP")
        self.root.geometry("900x650")
        self.dark_mode = False
        self.tasks = {}
        self.task_id_counter = 1
        self.incomplete_tasks = 0
        self.penalty_mode = False
        self.reminders_active = True

        self.setup_ui()
        self.reminder_thread = threading.Thread(target=self.check_reminders, daemon=True)
        self.reminder_thread.start()
    
    def setup_ui(self):
        self.setup_theme()
        header_frame = tk.Frame(self.root, bg = self.theme['accent'], padx=20, pady=15)
        header_frame.pack(fill="x")
        tk.Label(header_frame, text="Schedule Tracking App", font=('Helvetica', 18, 'bold'), bg=self.theme["accent"], fg='white').pack(side='left')
        stats_frame = tk.Frame(self.root, bg=self.theme['bg'], padx=20, pady=10)
        stats_frame.pack(fill="x")
        self.stats_label = tk.Label(stats_frame, text="Tasks : 0 | Incomplete : 0 | Penalties : 0", font=("Helvetica", 12), bg=self.theme["bg"], fg=self.theme["fg"])
        self.stats_label.pack(side='left')

        input_frame = tk.Frame(self.root, bg=self.theme['bg'], padx=20, pady=15)
        input_frame.pack(fill='x')
        tk.Label(input_frame, text='Task Decription:',font=('Helvetica', 12), bg=self.theme['bg'], fg= self.theme['fg']).grid(row=0, column=2, sticky="w", padx=(20,0))
        self.due_date_entry = DateEntry(input_frame, width=15, font=('Helvetica', 12), background='darkblue', foreground='white', date_pattern='yyyy-mm-dd')
        self.due_date_entry.grid(row=0, column=3, padx=10)
        self.due_date_entry.insert(0, datetime.now().strftime("%Y-%m-%d"))
        tk.Label(input_frame, text="Due Time:", font=('Helvetica', 12), bg=self.theme['bg'], fg= self.theme['fg']).grid(row=0, column=4, sticky="w", padx=(20,0))
        self.due_time_entry = tk.Entry(input_frame, width=10, font=("Helvetica", 12), relief='flat')
        self.due_time_entry.grid(row=0, column=5, padx=10)
        self.due_time_entry.insert(0, '23:59')

        add_button = tk.Button(input_frame, text="Add Task", command=self.add_task, bg=self.theme["accent"], fg="white", relief="flat", font=("Helvetica", 12), padx=15, pady=5)
        add_button.grid(row=0, column=6, padx=(20,0))

        list_frame = tk.Frame(self.root, bg=self.theme['bg'], padx=20, pady=10)
        list_frame.pack(fill="both", expand=True)
        self.task_tree = ttk.Treeview(list_frame, columns=("Id", "Description", "Due_Date", "Status", "Penalty"), show="headings", selectmode="browse")
        self.task_tree.heading("Id", text="Id")
        self.task_tree.heading("Description", text="Description")
        self.task_tree.heading("Due_Date", text="Due_Date")
        self.task_tree.heading("Status", text="Status")
        self.task_tree.heading("Penalty", text="Penalty")
        tk.Label(input_frame, text='Task Description:', font=('Helvetica', 12), bg=self.theme['bg'], fg=self.theme['fg']).grid(row=0, column=0, sticky='w')
        self.task_entry = tk.Entry(input_frame, width=30, font=('Helvetica', 12), relief='flat')
        self.task_entry.grid(row=0, column=1, padx=10)


        self.task_tree.column("Id", width=50, anchor="center")
        self.task_tree.column("Description", width=300, anchor="w")
        self.task_tree.column("Due_Date", width=120, anchor="center")
        self.task_tree.column("Status", width=100, anchor="center")
        self.task_tree.column("Penalty", width=80, anchor="center")

        self.task_tree.pack(fill="both", expand=True, side="left")
        scrollbar = ttk.Scrollbar(list_frame, orient="vertical", command=self.task_tree.yview)
        scrollbar.pack(side="right", fill="y")
        self.task_tree.configure(yscrollcommand=scrollbar.set)

        action_frame = tk.Frame(self.root, bg=self.theme["bg"], padx=20, pady=10)
        action_frame.pack(fill="x")
        complete_button = tk.Button(action_frame, text="Mark Complete", command=self.mark_complete, bg="#5cb85c", fg="white", relief="flat", font=("Helvetica", 12), padx=15, pady=5)
        complete_button.pack(side="left", padx=5)

        delete_button = tk.Button(action_frame, text="Delete Task",command=self.delete_task, bg = "#d9543f", fg="white", relief="flat", font=("Helvetica", 12), padx=15, pady=5)
        delete_button.pack(side="left", padx=5)

        reminder_button = tk.Button(action_frame, text="Toggle Reminders", command=self.toggle_reminders, bg="#f0ad4e", fg="white", relief="flat", font=("Helvetica",12), padx=15, pady=5)
        reminder_button.pack(side="left", padx=5)

        theme_button = tk.Button(action_frame, text="Toggle Dark/Light Mode", command=self.toggle_theme, bg="#007bff", fg="White", font=("Helvetica", 12), relief="flat", padx=15, pady=5)
        theme_button.pack(side="left", padx=5)

        penalty_frame = tk.Frame(self.root, bg=self.theme["bg"], padx=20, pady=10)
        penalty_frame.pack(fill="x")

        self.penalty_label = tk.Label(penalty_frame, text="Penalty Status: No Penalties Yet!", font=("Helvetica", 12), bg=self.theme["bg"], fg="#d9534f")
        self.penalty_label.pack(side="left")
        self.task_entry = tk.Entry(input_frame, width=40, font=("Helvetica", 12), relief="flat")
        self.task_entry.grid(row=0, column=1, padx=10)
        self.root.bind('<Return>', lambda event: self.add_task())
    def setup_theme(self):
        if self.dark_mode:
            self.theme = {
                "bg": "#2d2d2d",
                "fg" : "white",
                "accent" : "#4a6fa5"
            }
        else:
            self.theme = {
                "bg" : "#f0f2f5",
                "fg" : "#333333",
                "accent" : "#4a6fa5"
            }

    def add_task(self):
        description = self.task_entry.get().strip()
        due_date = self.due_date_entry.get().strip()
        due_time = self.due_time_entry.get().strip()

        if not description:
            messagebox.showwarning("Warning", "Task Description cannot be empty!")
            return
            
        try:
            datetime.strptime(due_date, "%Y-%m-%d")
            datetime.strptime(due_time, "%H:%M")
        except ValueError:
                messagebox.showwarning("Warning", "Invalid Date or time Format! Use YYYY-MM-DD and HH:MM")
                return
        
        task_id = max(self.tasks.keys(), default=0) + 1 
        penalty = "Yes" if self.penalty_mode else "No"

        task = {
                "id" : task_id,
                "Description" : description,
                "Due_Date" : due_date,
                "Due_Time" : due_time,
                "Status" : "Pending",
                "Penalty" : penalty,
                "Completed" : False
            }
        self.tasks[task_id] = task
        self.task_tree.insert("", "end", iid=str(task_id), values=(task_id, description, f"{due_date} {due_time}", "Pending", penalty))
        self.task_entry.delete(0, "end")
        self.update_stats()

        if self.penalty_mode:
             self.penalty_mode = False
             self.penalty_label.config(text = "Penalty status: Penalty Task Added", fg ="#5cb85c")
        
    def mark_complete(self):
        selected_item = self.task_tree.selection()
        if not selected_item:
            messagebox.showwarning("Warning", "Please select a task to mark as complete!")
            return
        item = self.task_tree.item(selected_item)
        task_id = item["values"][0]  # This gets the ID from Treeview
        if task_id in self.tasks:
            task = self.tasks[task_id]
            task["Status"] = "Completed"
            task["Completed"] = True
            self.task_tree.item(selected_item, values=(
                task["id"],
                task["Description"],
                f"{task['Due_Date']} {task['Due_Time']}",
                "Completed",
                task["Penalty"]
                ))
        self.update_stats()


    def delete_task(self):
        selected_item = self.task_tree.selection()
        if not selected_item:
            messagebox.showwarning("Warning", "Please select a task to delete!")
            return
        task_id = int(selected_item[0])
        if task_id in self.tasks:
            if not self.tasks[task_id]["Completed"]:
                self.incomplete_tasks += 1
            del self.tasks[task_id]  # delete from the dictionary
            
            self.task_tree.delete(selected_item)  # delete from the Treeview
            self.update_stats()
        
    ''' item = self.task_tree.item(selected_item)
        task_id = item["values"][0]
        
        for i, task in enumerate(self.tasks):
            if task["id"] == task_id:
                #if not task["Completed"]:
                 #   self.incomplete_tasks += 1
                del self.tasks[i]
                break
            
        self.task_tree.delete(selected_item)
        self.update_stats()'''

    def toggle_reminders(self):
        self.reminders_active = not self.reminders_active
        status = "ON" if self.reminders_active else "OFF"
        messagebox.showinfo("Reminders", f"Reminders are now {status}")
    def check_reminders(self):
        while True:
            if self.reminders_active:
                now = datetime.now()
                for task in self.tasks:
                    if not task["Completed"]:
                        due_datetime = datetime.strptime(f"{task["Due_Date"]} {task["Due_Time"]}", "%Y-%m-%d %H:%M")
                        if now >= due_datetime:
                            self.show_reminder(task)
            time.sleep(60)
            #self.task_entry = tk.Entry(input_frame, width=40, font=("Helvetica", 12), relief="flat")
            #self.task_entry.grid(row=0, column=1, padx=10)


    def show_reminder(self, task):
         if not self.reminders_active:
            return
         self.root.after(0, lambda:messagebox.showwarning("Reminder", f"Task Overdue!\n\nDescription : {task["Description"]}\nDue: {task["Due_Date"]}{task["Due_Time"]}"))

    def update_stats(self):
        total_tasks = len(self.tasks)
        incomplete = sum(1 for task in self.tasks.values() if not task["Completed"])
        penalties = sum(1 for task in self.tasks.values() if task["Penalty"] == "Yes")

        self.stats_label.config(text=f"Tasks : {total_tasks} | Incomplete : {incomplete} | Penalties : {penalties}")

        if incomplete >= 3 and not self.penalty_mode:
            self.penalty_mode = True
            self.penalty_label.config(text="Penalty Status: Add a Penalty Task!", fg="#d9534f")
            messagebox.showwarning("Penalty!", "You are 3 or more incomplete tasks. Your next task will be marked as a Penalty.")

    def toggle_theme(self):
            self.dark_mode = not self.dark_mode
            self.setup_theme()
            self.refresh_ui()

    def refresh_ui(self):
        self.root.config(bg=self.theme["bg"])
        for widget in self.root.winfo_children():
            try:
                widget.config(bg=self.theme["bg"], fg=self.theme["fg"])
            except tk.TclError:
                widget.config(bg=self.theme["bg"])

        for item in self.task_tree.get_children():
            self.task_tree.item(item, tags=("task",))
            self.task_tree.tag_configure("task", background = self.theme['bg'], foreground = self.theme['fg'])

if __name__=="__main__":
    root = tk.Tk()
    app = EnhancedScheduleTrackerApp(root)
    root.mainloop()






















