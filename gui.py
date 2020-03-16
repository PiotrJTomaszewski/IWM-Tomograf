import tkinter as tk
import numpy as np
import PIL.Image
import PIL.ImageTk

# TODO: Set default values

DELTA_ALPHA_STEP_MIN = 0.1
DELTA_ALPHA_STEP_MAX = 10
DELTA_ALPHA_STEP_INCREMENT = 0.1

NUMBER_OF_DETECTORS_MIN = 1
NUMBER_OF_DETECTORS_MAX = 100
NUMBER_OF_DETECTORS_INCREMENT = 1

SPREAD_MIN = 0.1
SPREAD_MAX = 10
SPREAD_INCREMENT = 0.1

IMAGE_WIDTH = 300
IMAGE_HEIGHT = 300


class TomographGUI:
    def __init__(self, master, input_image_confirm_clbk, sim_options_confirm_clbk, radon_next_step_clbk):
        self.master = master
        master.title('Symulator tomografu')
        # Create widgets
        self._setup_input_image_selection(input_image_confirm_clbk)
        self._setup_simulation_options(sim_options_confirm_clbk)
        self._setup_radon_steps(radon_next_step_clbk)
        self._setup_sinogram()

    def _setup_input_image_selection(self, input_image_confirm_clbk):
        self.input_image_frame = tk.LabelFrame(master=self.master, text='Obraz wejściowy')
        self.input_image_selection = tk.Listbox(master=self.input_image_frame)
        self.input_image_confirm = tk.Button(master=self.input_image_frame, text='Zatwierdź',
                                             command=input_image_confirm_clbk)
        self.input_image = tk.Canvas(master=self.input_image_frame, width=IMAGE_WIDTH, height=IMAGE_HEIGHT)

        self.input_image_frame.grid(row=0, column=0)
        self.input_image_selection.pack()
        self.input_image_confirm.pack()
        self.input_image.pack()

    def _setup_simulation_options(self, sim_options_confirm_clbk):
        self.settings_frame = tk.LabelFrame(master=self.master, text='Opcje')
        # Delta alpha step
        self.delta_alpha_step_label = tk.Label(master=self.settings_frame, text='Krok Δα układu emiter/detektor')
        self.delta_alpha_step = tk.Scale(master=self.settings_frame, from_=DELTA_ALPHA_STEP_MIN,
                                         to=DELTA_ALPHA_STEP_MAX, resolution=DELTA_ALPHA_STEP_INCREMENT,
                                         orient=tk.HORIZONTAL)
        # Number of detectors (n)
        self.number_of_detectors_label = tk.Label(master=self.settings_frame, text='Liczba detektorów (n)')
        self.number_of_detectors = tk.Scale(master=self.settings_frame, from_=NUMBER_OF_DETECTORS_MIN,
                                            to=NUMBER_OF_DETECTORS_MAX, resolution=NUMBER_OF_DETECTORS_INCREMENT,
                                            orient=tk.HORIZONTAL)
        # Emitter / detector spread (l)
        self.detectors_spread_label = tk.Label(master=self.settings_frame,
                                               text='Rozwartość / rozpiętość układu emiter/detektor (l)')
        self.detectors_spread = tk.Scale(master=self.settings_frame, from_=SPREAD_MIN, to=SPREAD_MAX,
                                         resolution=SPREAD_INCREMENT, orient=tk.HORIZONTAL)
        self.options_confirm = tk.Button(master=self.settings_frame, text='Zatwierdź',
                                         command=sim_options_confirm_clbk)

        self.options_image = tk.Canvas(master=self.settings_frame, width=IMAGE_WIDTH, height=IMAGE_HEIGHT)
        self.settings_frame.grid(row=1, column=0)
        self.delta_alpha_step_label.pack()
        self.delta_alpha_step.pack()
        self.number_of_detectors_label.pack()
        self.number_of_detectors.pack()
        self.detectors_spread_label.pack()
        self.detectors_spread.pack()
        self.options_confirm.pack()
        self.options_image.pack()

    def _setup_radon_steps(self, radon_next_step_clbk):
        self.radon_frame = tk.LabelFrame(master=self.master, text='Transformata Radona')
        self.show_steps = tk.Checkbutton(master=self.radon_frame, text='Pokazuj kroki pośrednie', onvalue=1, offvalue=0)
        self.simulation_step_image = tk.Canvas(master=self.radon_frame, width=IMAGE_WIDTH, height=IMAGE_HEIGHT)
        self.next_sim_step = tk.Button(master=self.radon_frame, text='Następny krok', command=radon_next_step_clbk)

        self.radon_frame.grid(row=0, column=1)
        self.show_steps.pack()
        self.simulation_step_image.pack()
        self.next_sim_step.pack()

    def _setup_sinogram(self):
        self.singogram_frame = tk.LabelFrame(master=self.master, text='Singoram')
        self.sinogram_image = tk.Canvas(master=self.singogram_frame, width=IMAGE_WIDTH, height=IMAGE_HEIGHT)

        self.singogram_frame.grid(row=1, column=1)
        self.sinogram_image.pack()

    def display_image(self, image_array, image_type):
        # PIL doesn't support floating point inputs
        if image_array.dtype == np.float64:
            image_array = (image_array * 255).astype(np.uint8)
        if image_type == 'input':
            canvas = self.input_image
        elif image_type == 'options':
            canvas = self.options_image
        elif image_type == 'simulation_step':
            canvas = self.simulation_step_image
        elif image_type == 'singogram':
            canvas = self.sinogram_image
        else:
            print('This image type doesn\'t exist')
            return
        # Convert image from numpy array to PIL image and resize it
        img = PIL.Image.fromarray(image_array).resize((IMAGE_WIDTH, IMAGE_HEIGHT), PIL.Image.ANTIALIAS)
        img = PIL.ImageTk.PhotoImage(image=img)
        canvas.create_image(0, 0, anchor=tk.NW, image=img)
        canvas.photo = img

    def set_available_input_images(self, image_names):
        # Clear old options - probably won't be necessary
        self.input_image_selection.delete(0, last=tk.END)
        for i, name in enumerate(image_names):
            self.input_image_selection.insert(i, name)
        # Set the first item selected
        # TODO: Doesn't work
        self.input_image_selection.activate(0)

    def get_selected_input_image(self):
        return self.input_image_selection.curselection()

    def get_simulations_options(self):
        delta_alpha_step = self.delta_alpha_step.get()
        number_of_detectors = self.number_of_detectors.get()
        detectors_spread = self.detectors_spread.get()
        return delta_alpha_step, number_of_detectors, detectors_spread

# def main():
#     from tomograph import open_all_images
#
#     images = open_all_images()
#     img = images['Shepp_logan']
#     root = tk.Tk()
#     gui = Tomograph_GUI(root)
#     gui.display_image(img, 'input')
#
#     root.mainloop()

#
# if __name__ == '__main__':
#     main()
