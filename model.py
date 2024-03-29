from keras.models import Model
from keras.layers import Input, Dense, Conv2D, BatchNormalization
from keras.layers import Activation, Concatenate, Reshape, Dropout
from keras.layers import Flatten, MaxPooling2D

def dense_block(x, blocks, growth_rate, dropout_rate):
    """A dense block."""
    for _ in range(blocks):
        x = conv_block(x, growth_rate)
        if dropout_rate:
            x = Dropout(dropout_rate)(x)
    return x

def conv_block(x, growth_rate):
    """A building block for a dense block."""
    x1 = BatchNormalization()(x)
    x1 = Activation('elu')(x1)
    x1 = Conv2D(growth_rate, 3, padding='same', kernel_initializer='he_normal')(x1)
    x = Concatenate()([x, x1])
    return x

def transition_block(x, reduction):
    """A transition block."""
    x = BatchNormalization()(x)
    x = Activation('relu')(x)
    x = Conv2D(int(x.shape[-1] * reduction), 1, padding='same', kernel_initializer='he_normal')(x)
    return x

def create_model(input_shape, blocks=[6, 12], growth_rate=12, reduction=0.5, dropout_rate = 0.2, num_classes=None):
    """Instantiates the DenseNet architecture."""
    img_input = Input(shape=input_shape)

    # Reshape the input for compatibility with Conv2D layers
    x = Reshape((*input_shape, 1))(img_input)

    # Initial convolution layer
    x = Conv2D(16, 3, activation='elu')(x)      # 16 filter convolution
    x = MaxPooling2D((2, 2))(x)

    x = Conv2D(64, 3, activation='elu') (x)     # 32 filter convolution
    x = MaxPooling2D((2, 2))(x)

    x = Conv2D(128, 3,activation='elu') (x)     # 64 filter convolution
    x = MaxPooling2D((2, 2))(x)


    # Dense blocks and transition blocks
    for i, block in enumerate(blocks):
        x = dense_block(x, block, growth_rate, dropout_rate)
        if i != len(blocks) - 1:
            x = transition_block(x, reduction)

    # Final Layers
    
    x = Flatten()(x)#(final)
            
    x = Dense(64, activation='elu')(x)
    x = BatchNormalization()(x)
    x = Dropout(0.3)(x)

    x = Dense(64, activation='elu')(x)
    x = BatchNormalization()(x)
    x = Dropout(0.3)(x)

    out = Dense(num_classes, activation='softmax')(x)

    # Create model
    model = Model(img_input, out)
    return model
