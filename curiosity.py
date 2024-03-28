import os
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'
os.environ['TF_XLA_FLAGS'] = '--tf_xla_enable_xla_devices=false'
import numpy as np
import cv2
#import matplotlib.pyplot as plt
from keras.datasets import mnist
from keras.layers import Input, Dense, Conv2D, MaxPooling2D, UpSampling2D
from keras.models import Model
from threading import Thread
from PIL import Image
from time import sleep

class curiosity():

    difference_margin=0.8 #difference btween the sum of the two sides, if the value is greather than this, it would start moving to sides
    shock_margin=25 # if greater than this value, the algo will stop and watch
    procesimgsize=64#28#42
    saved_model_uri="tmp/saved_model"

    def __init__(self,savemodel=True,img_width=100,img_height=100):
        self.savemodel=savemodel
        print("curiosity NN init")

        self.c=0
        self.last_state="STOP"
        self.state="STOP"
        self.state_vals=[0,0]

        self.img_width = img_width
        self.img_height = img_height

        self.autoencoder=self.model()

    def prepare_image(self, image):
        image = np.asarray(Image.open(image))
        # Normalize pixel values to [0, 1]
        image = image.astype('float32') / 255.0
        image = np.expand_dims(image, axis=0)
        return image

    def predict_and_calculate_mse(self,image):
        try:
            decoded_image = self.autoencoder.predict(image,verbose=0)
            mse = np.mean((image - decoded_image) ** 2)
        except Exception as e:
            print("predict_and_calculate_mse EXCEPTION!!!:",e)
            print("")
            self.end()

        return mse

    def update_model_with_new_image(self,image, epochs=5):
        try:
            self.autoencoder.fit(image, image, epochs=epochs, verbose=0)
        except Exception as e:
            print("update_model_with_new_image EXCEPTION!!!:",e)
            print("")
            self.end()

    def model(self):
        if os.path.isfile(self.saved_model_uri) and self.savemodel:
            model = keras.models.load_model(self.saved_model_uri)
            return model
        else:
            input_img = Input(shape=(self.img_height, self.img_width, 3))

            params=64 # Number of filters
            size=6 # Kernel size for the convolution
            size2=2 # Pooling size

            # Encoder
            x = Conv2D(params, (size, size), activation='relu', padding='same')(input_img)
            x = MaxPooling2D((size2, size2), padding='same')(x)
            x = Conv2D(params, (size, size), activation='relu', padding='same')(x)
            encoded = MaxPooling2D((size2, size2), padding='same')(x)

            # Decoder
            x = Conv2D(params, (size, size), activation='relu', padding='same')(encoded)
            x = UpSampling2D((size2, size2))(x)
            x = Conv2D(params, (size, size), activation='relu', padding='same')(x)
            x = UpSampling2D((size2, size2))(x)
            decoded = Conv2D(3, (size, size), activation='sigmoid', padding='same')(x)

            autoencoder = Model(input_img, decoded)

            autoencoder.compile(optimizer='adam', loss='mean_squared_error')
            
            return autoencoder


    def remap_image_colorspace_bad(self,image):
        return cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

    def remap_image_colorspace(self,image):
        # Split the color channels
        b, g, r = cv2.split(image)

        # Adjust the color balance by enhancing green channel
        adjusted_green = np.clip(g * 1.5, 0, 255).astype(np.uint8)

        # Merge the color channels to obtain the resulting image
        result = cv2.merge((b, adjusted_green, r))

        return result

    def remap_image_colorspace_weird(self,image):
        # Define the color correction matrix
        color_correction_matrix = np.array([[1.1, -0.1, -0.1],
                                            [-0.1, 1.6, -0.1],
                                            [-0.1, -0.3, 1.3]])

        # Reshape the image into a 2D array
        flattened_image = image.reshape((-1, 3))

        # Apply the color correction matrix to each pixel
        corrected_image = np.dot(flattened_image, color_correction_matrix.T).astype(np.uint8)

        # Reshape the image back to the original shape
        corrected_image = corrected_image.reshape(image.shape)

        return corrected_image

    def end(self):
        if self.savemodel:
            self.autoencoder.save(self.saved_model_uri)
            #self.cap.release()

