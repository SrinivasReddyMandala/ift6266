from blocks.bricks import Rectifier, Logistic, FeedforwardSequence, Initializable, MLP, BatchNormalizedMLP
from blocks.bricks.conv import Convolutional, ConvolutionalSequence, Flattener, MaxPooling
from blocks.graph import ComputationGraph, apply_batch_normalization, get_batch_normalization_updates
from blocks.initialization import Constant, Uniform
import numpy

from theano import tensor

class VGGNet(FeedforwardSequence, Initializable):

    def __init__(self, image_dimension, **kwargs):

        layers = []
        
        #############################################
        # a first block with 2 convolutions of 64 (3, 3) filters
        layers.append(Convolutional((3, 3), 64, border_mode='half', name='conv_1_1'))
        layers.append(Rectifier())
        layers.append(Convolutional((3, 3), 64, border_mode='half', name='conv_1_2'))
        layers.append(Rectifier())

        # maxpool with size=(2, 2)
        layers.append(MaxPooling((2, 2)))

        #############################################
        # a 2nd block with 3 convolutions of 128 (3, 3) filters
        layers.append(Convolutional((3, 3), 128, border_mode='half', name='conv_2_1'))
        layers.append(Rectifier())
        layers.append(Convolutional((3, 3), 128, border_mode='half', name='conv_2_2'))
        layers.append(Rectifier())
        
        # maxpool with size=(2, 2)
        layers.append(MaxPooling((2, 2)))

        #############################################
        # a 3rd block with 4 convolutions of 256 (3, 3) filters
        layers.append(Convolutional((3, 3), 256, border_mode='half', name='conv_3_1'))
        layers.append(Rectifier())
        layers.append(Convolutional((3, 3), 256, border_mode='half', name='conv_3_2'))
        layers.append(Rectifier())
        layers.append(Convolutional((3, 3), 256, border_mode='half', name='conv_3_3'))
        layers.append(Rectifier())
        layers.append(Convolutional((3, 3), 256, border_mode='half', name='conv_3_4'))
        layers.append(Rectifier())
        
        # maxpool with size=(2, 2)
        layers.append(MaxPooling((2, 2)))

        #############################################
        # a 4th block with 4 convolutions of 512 (3, 3) filters
        layers.append(Convolutional((3, 3), 512, border_mode='half', name='conv_4_1'))
        layers.append(Rectifier())
        layers.append(Convolutional((3, 3), 512, border_mode='half', name='conv_4_2'))
        layers.append(Rectifier())
        layers.append(Convolutional((3, 3), 512, border_mode='half', name='conv_4_3'))
        layers.append(Rectifier())
        layers.append(Convolutional((3, 3), 512, border_mode='half', name='conv_4_4'))
        layers.append(Rectifier())
        
        # maxpool with size=(2, 2)
        layers.append(MaxPooling((2, 2)))

        #############################################
        # a 5th block with 4 convolutions of 512 (3, 3) filters
        layers.append(Convolutional((3, 3), 512, border_mode='half', name='conv_5_1'))
        layers.append(Rectifier())
        layers.append(Convolutional((3, 3), 512, border_mode='half', name='conv_5_2'))
        layers.append(Rectifier())
        layers.append(Convolutional((3, 3), 512, border_mode='half', name='conv_5_3'))
        layers.append(Rectifier())
        layers.append(Convolutional((3, 3), 512, border_mode='half', name='conv_5_4'))
        layers.append(Rectifier())
        
        # maxpool with size=(2, 2)
        layers.append(MaxPooling((2, 2)))

        self.conv_sequence = ConvolutionalSequence(layers, 3, image_size=image_dimension)

        flattener = Flattener()

        self.top_mlp = BatchNormalizedMLP(activations=[Rectifier(), Rectifier(), Rectifier(), Logistic()], dims=[4096, 4096, 1000, 1])

        application_methods = [self.conv_sequence.apply, flattener.apply, self.top_mlp.apply]

        super(VGGNet, self).__init__(application_methods, biases_init=Constant(0), weights_init=Uniform(width=.1), **kwargs)


    def _push_allocation_config(self):
        self.conv_sequence._push_allocation_config()
        conv_out_dim = self.conv_sequence.get_dim('output')

        self.top_mlp.dims = [numpy.prod(conv_out_dim)] + self.top_mlp.dims



def get_model(X, batch_size, image_dimension):

    vgg = VGGNet(image_dimension)

    vgg.push_initialization_config()
    vgg.initialize()

    output = vgg.apply(X)

    output_test1 = vgg.apply(X[:,:,:image_dimension[0],:image_dimension[1]])
    output_test2 = vgg.apply(X[:,:,-image_dimension[0]:,-image_dimension[1]:])

    output_test = tensor.switch(tensor.ge(tensor.abs_(output_test1-0.5), tensor.abs_(output_test2-0.5)), output_test1, output_test2)

    return output, output_test
