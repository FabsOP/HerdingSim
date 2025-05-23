import tkinter as tk
import copy
from boid import default_behaviours, behaviours, param_short_names,updateParamBoundaries
import boid
import time

class BehaviourTab(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent, bg="#F5FBEF")
        self.pack(fill="both", expand=True)

        self.species = list(default_behaviours.keys())
        self.selection = self.species[0]
        self.selector_idx = 0

        header_frame = tk.Frame(self, bg="#F5FBEF")
        header_frame.pack(fill="x", pady=(5, 0))

        selector_frame = tk.Frame(header_frame, bg="#F5FBEF")
        selector_frame.pack(pady=2)

        tk.Button(selector_frame, text="<", bg="#E2F0D9", fg="#4C6B32", font=("Comic Sans MS", 8, "bold"),
                  relief="raised", bd=1, width=1, command=lambda: self.changeSelection("<")).pack(side=tk.LEFT, padx=2)

        self.species_label = tk.Label(selector_frame, width=8, text=self.species[self.selector_idx],
                                      bg="#F5FBEF", fg="#4C6B32", font=("Comic Sans MS", 9, "bold"))
        self.species_label.pack(side=tk.LEFT, padx=2)

        tk.Button(selector_frame, text=">", bg="#E2F0D9", fg="#4C6B32", font=("Comic Sans MS", 8, "bold"),
                  relief="raised", bd=1, width=1, command=lambda: self.changeSelection(">")).pack(side=tk.LEFT, padx=2)

        reset_button = tk.Button(selector_frame, text="Reset", bg="#E2F0D9", fg="#4C6B32",
                                 font=("Comic Sans MS", 8), relief="raised", bd=1,
                                 command=self.reset_to_default)
        reset_button.pack(side=tk.LEFT, padx=(10, 2))

        self.behaviour_settings_frame = tk.Frame(self, bg="#F5FBEF")
        self.behaviour_settings_frame.pack(fill="both", expand=True, padx=5, pady=5)

        self.sliders = {}
        self.value_entries = {}  # Store entry widgets
        self.create_sliders()

    def create_sliders(self):
        for widget in self.behaviour_settings_frame.winfo_children():
            widget.destroy()

        row = 0
        self.sliders = {}
        self.value_entries = {}

        header_frame = tk.Frame(self.behaviour_settings_frame, bg="#F5FBEF")
        header_frame.grid(row=row, column=0, sticky="ew", pady=(0, 2))
        tk.Label(header_frame, text="Parameter", width=10, bg="#F5FBEF",
                 fg="#4C6B32", font=("Comic Sans MS", 8, "bold")).grid(row=0, column=0)
        tk.Label(header_frame, text="Value", width=3, bg="#F5FBEF",
                 fg="#4C6B32", font=("Comic Sans MS", 8, "bold")).grid(row=0, column=1)

        row += 1
        visible_frame = tk.Frame(self.behaviour_settings_frame, bg="#F5FBEF")
        visible_frame.grid(row=row, column=0, sticky="ew")

        param_row = 0
        for param in default_behaviours[self.selection]:
            if isinstance(behaviours[self.selection][param], int): 
                continue
            
            min_val, max_val, step, val_type, val = behaviours[self.selection][param]

            param_frame = tk.Frame(visible_frame, bg="#F5FBEF")
            param_frame.grid(row=param_row, column=0, sticky="ew", pady=2)

            # Parameter label
            tk.Label(param_frame, text=param_short_names[param], width=10, bg="#F5FBEF",
                     fg="#4C6B32", font=("Comic Sans MS", 8)).grid(row=0, column=0, sticky="w")

            # Value entry field
            value_str = f"{val:.1f}" if val_type == float else str(int(val))
            value_var = tk.StringVar(value=value_str)
            value_entry = tk.Entry(param_frame, textvariable=value_var, width=5, bg="#FFFFFF",
                                  fg="#4C6B32", font=("Comic Sans MS", 8), bd=1,
                                  justify=tk.CENTER)
            value_entry.grid(row=0, column=1, padx=(0, 3))
            value_entry.bind("<Return>", lambda event, p=param, v=value_var, t=val_type: 
                           self.update_from_entry(p, v, t))
            value_entry.bind("<FocusOut>", lambda event, p=param, v=value_var, t=val_type: 
                           self.update_from_entry(p, v, t))
            
            self.value_entries[param] = value_var

            # Slider
            resolution = step
            slider = tk.Scale(
                param_frame,
                from_=min_val,
                to=max_val,
                resolution=resolution,
                orient=tk.HORIZONTAL,
                bg="#E2F0D9",
                fg="#4C6B32",
                troughcolor="#C1E1C1",
                highlightbackground="#F5FBEF",
                highlightcolor="#A9C46C",
                activebackground="#A9C46C",
                font=("Comic Sans MS", 7),
                sliderrelief=tk.FLAT,
                bd=1,
                length=90,
                showvalue=False,
                command=lambda v, p=param, t=val_type: self.update_from_slider(v, p, t)
            )
            slider.grid(row=0, column=2, padx=(2, 0))
            slider.set(val)
            self.sliders[param] = slider

            param_row += 1

    def update_from_entry(self, param, value_var, val_type):
        """Update the value when the entry is changed"""
        try:
            # Try to convert the entry value to the appropriate type
            if val_type == float:
                new_val = float(value_var.get())
                # Format to one decimal place for display consistency
                value_var.set(f"{new_val:.1f}")
            else:  # for int values
                new_val = int(float(value_var.get()))  # Convert via float for robustness
                value_var.set(str(new_val))
            
            # Ensure value is within bounds
            min_val = behaviours[self.selection][param][0]
            max_val = behaviours[self.selection][param][1]
            
            if new_val < min_val:
                new_val = min_val
                if val_type == float:
                    value_var.set(f"{new_val:.1f}")
                else:
                    value_var.set(str(int(new_val)))
            elif new_val > max_val:
                new_val = max_val
                if val_type == float:
                    value_var.set(f"{new_val:.1f}")
                else:
                    value_var.set(str(int(new_val)))
                
            # Update the behaviour value
            behaviours[self.selection][param][4] = new_val
            
            # Update the slider to match
            self.sliders[param].set(new_val)
            
            boid.lastModified= {"species": self.selected, "parameter": param, "time": time.time()}
            updateParamBoundaries()
            self.refresh_sliders()
            
        except ValueError:
            # Restore the previous valid value if conversion fails
            old_val = behaviours[self.selection][param][4]
            if val_type == float:
                value_var.set(f"{old_val:.1f}")
            else:
                value_var.set(str(int(old_val)))

    def update_from_slider(self, val, param, val_type):
        """Update the value when the slider is moved"""
        typed_val = val_type(float(val))
        
        # Update the entry field
        if val_type == float:
            self.value_entries[param].set(f"{typed_val:.1f}")
        else:
            self.value_entries[param].set(str(int(typed_val)))
        
        # Update the value in behaviours
        behaviours[self.selection][param][4] = typed_val
        
        # Update dependent parameters
        boid.lastModified = {"species": self.selection, "parameter": param, "time": time.time()}
        updateParamBoundaries()
        self.refresh_sliders()

    def refresh_sliders(self):
        # Update slider bounds and values to reflect current parameter constraints
        for key, slider in self.sliders.items():
            param_config = behaviours[self.selection][key]
            min_val = param_config[0]
            max_val = param_config[1]
            current_val = param_config[4]
            
            # Only update if there's a change
            if float(slider.cget("from")) != min_val:
                slider.config(from_=min_val)
            if float(slider.cget("to")) != max_val:
                slider.config(to_=max_val)
            
            # Ensure value is within bounds
            if current_val < min_val:
                param_config[4] = min_val
                slider.set(min_val)
                # Update entry field as well
                val_type = param_config[3]
                if val_type == float:
                    self.value_entries[key].set(f"{min_val:.1f}")
                else:
                    self.value_entries[key].set(str(int(min_val)))
            elif current_val > max_val:
                param_config[4] = max_val
                slider.set(max_val)
                # Update entry field as well
                val_type = param_config[3]
                if val_type == float:
                    self.value_entries[key].set(f"{max_val:.1f}")
                else:
                    self.value_entries[key].set(str(int(max_val)))

    def changeSelection(self, direction):
        if direction == ">":
            self.selector_idx = (self.selector_idx + 1) % len(self.species)
        elif direction == "<":
            self.selector_idx = (self.selector_idx - 1) % len(self.species)

        self.selection = self.species[self.selector_idx]
        self.species_label.config(text=self.selection)
        self.create_sliders()

    def reset_to_default(self):
        behaviours[self.selection] = copy.deepcopy(default_behaviours[self.selection])
        self.create_sliders()