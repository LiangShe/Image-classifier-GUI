import wx
import os
import json
import glob

class ImageClassifier(wx.Frame):

    def __init__(self, parent, title):
        super().__init__(parent, title=title, size=(1800, 900))
        
        self.Bind(wx.EVT_CLOSE, self.OnClose)
        self.InitUI()

    def InitUI(self):

        self.config_file = "config.json"
        
        if os.path.isfile(self.config_file):
            self.load_config()
        else:
            self.default_data_path = ""
            self.save_config()

        self.image_label_file = "image_labels.json"
        self.image_label_file_full_path = os.path.join(self.default_data_path, self.image_label_file)
        self.image_labels = {'classes': [], 'labels': {}}
        self.image_names = []
        self.current_image_index = 0

        self.font = wx.Font(20, wx.SWISS, wx.NORMAL, wx.NORMAL)

        self.class_checkboxes = []
        self.checkbox_size = (200, 50)

        self.panel = wx.Panel(self)
        self.panel.Bind(wx.EVT_KEY_DOWN, self.OnKeyDown)

        # Create a UI to display the image
        self.image = wx.StaticBitmap(self.panel, wx.ID_ANY)
        # self.image.SetScaleMode(2)

        # Create a button to open an image dataset
        open_button = wx.Button(self.panel, wx.ID_OPEN, label="Open image dataset")
        open_button.SetFont(self.font)
        open_button.Bind(wx.EVT_BUTTON, self.OnOpenImageSet)

        # Create a button to auto classify the image
        classify_button = wx.Button(self.panel, wx.ID_OK, label="Audo classify")
        classify_button.SetFont(self.font)
        classify_button.Bind(wx.EVT_BUTTON, self.OnClassifyImage)

        # Add a button to add a user-defined class
        add_class_button = wx.Button(self.panel, wx.ID_ADD, label="Add Class")
        add_class_button.SetFont(self.font)
        add_class_button.Bind(wx.EVT_BUTTON, self.OnAddClass)
        
        # Layout the controls
        self.sizer_right = wx.BoxSizer(wx.VERTICAL)
        self.sizer_right.Add(open_button, 0, wx.ALIGN_CENTER)
        self.sizer_right.Add(classify_button, 0, wx.ALIGN_CENTER)
        self.sizer_right.Add(wx.StaticLine(self.panel, -1), 0, wx.EXPAND)
        self.sizer_right.Add(add_class_button, 0, wx.ALIGN_CENTER)

        self.sizer_main = wx.BoxSizer(wx.HORIZONTAL)
        self.sizer_main.Add(self.image, 1, wx.ALL, 5)
        self.sizer_main.Add(self.sizer_right, 0, wx.ALIGN_TOP)
        self.panel.SetSizer(self.sizer_main)

        self.Centre()
        self.Show()

    def load_config(self):
        with open(self.config_file, "r") as f:
            config = json.load(f)
            self.default_data_path = config["default_data_path"]

    def save_config(self):
        config_dict = {"default_data_path": self.default_data_path}
        with open(self.config_file, "w") as f:
            json.dump(config_dict, f)
    
    def load_labels(self):
        self.image_label_file_full_path = os.path.join(self.default_data_path, self.image_label_file)
        if os.path.isfile(self.image_label_file_full_path):
            with open(self.image_label_file_full_path, "r") as f:
                self.image_labels = json.load(f)
                self.create_class_checkboxes()


    def save_labels(self):
        with open(self.image_label_file_full_path, "w") as f:
            json.dump(self.image_labels, f)
    
    def create_class_checkboxes(self):
        image_classes = self.image_labels["classes"]
        for image_class in image_classes:
            self.add_class_checkbox(image_class)

    def add_class_checkbox(self,image_class):
        checkbox = wx.CheckBox(self.panel, label=image_class, size=self.checkbox_size)
        checkbox.SetFont(self.font)
        checkbox.Bind(wx.EVT_CHECKBOX, self.OnCheckBox)
        self.class_checkboxes.append(checkbox)
        self.sizer_right.Add(checkbox, 0, wx.ALIGN_LEFT)

    # TODO: adaptive scale
    def scale_image(self, image):
        # scale the image, preserving the aspect ratio
        w = image.GetWidth()
        h = image.GetHeight()
        # w_panel = self.image.GetMaxWidth()
        # h_panel = self.image.GetMaxHeight()
        # print(w_panel, h_panel)
        # if w/h > w_panel/h_panel:
        #     w_new = w_panel
        #     h_new = w_panel * h / w
        # else:
        #     h_new = h_panel
        #     w_new = h_panel * w / h
        w_new = 1500
        h_new = int(w_new * h / w)
        return image.Scale(w_new, h_new)
    
    def LoadImage(self):
        
        # load current image label
        image_rel_path = self.image_names[self.current_image_index]
        image_label = self.image_labels['labels'][image_rel_path]

        # Load the image
        image_full_path = os.path.join(self.default_data_path, image_rel_path)
        image = wx.Image(image_full_path)
        image = self.scale_image(image)
        self.image.SetBitmap(wx.Bitmap(image))

        # Update the checkboxes
        for checkbox, label in zip(self.class_checkboxes, image_label):
            checkbox.SetValue(label)

    def OnOpenImageSet(self, event):
        dlg = wx.DirDialog(self, "Select image dataset folder", self.default_data_path)
        if dlg.ShowModal() == wx.ID_OK:
            self.default_data_path = dlg.GetPath()
            self.save_config()
            
            # Load the image labels
            self.load_labels()
            
            # find all images and add them to the dict
            images_full_path = glob.glob(os.path.join(self.default_data_path, "**/*.png"))
            images_rel_path = [os.path.relpath(imfp, self.default_data_path) for imfp in images_full_path]
            for imrp in images_rel_path:
                if imrp not in self.image_labels['labels']:
                    self.image_labels['labels'][imrp] = []

            # use image relative path as unique name
            self.image_names = images_rel_path

            self.LoadImage()


    def OnClassifyImage(self, event):
        # TODO: Implement image classification
        pass

    
    def OnKeyDown(self, event):
        keycode = event.GetKeyCode()
        print(keycode)
        if keycode == 27: # Esc key
            self.Close()
        elif keycode == 83: # S key
            self.save_labels()
            self.current_image_index += 1
            if self.current_image_index >= len(self.image_labels):
                self.current_image_index = 0
            self.LoadImage()

    def OnAddClass(self, event):
        dlg = wx.TextEntryDialog(self, "Enter class name")
        if dlg.ShowModal() == wx.ID_OK:
            class_name = dlg.GetValue()
            self.image_labels["classes"].append(class_name)
            self.add_class_checkbox(class_name)

    def OnCheckBox(self, event):
        self.image_labels['labels'][self.image_names[self.current_image_index]] = \
            [cb.GetValue() for cb in self.class_checkboxes]

    def OnClose(self, event):
        self.save_labels()
        self.Destroy() # close the window


if __name__ == "__main__":
    app = wx.App()
    frame = ImageClassifier(None, title="Image Classifier")
    app.MainLoop()
