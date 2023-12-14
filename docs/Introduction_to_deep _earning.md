# Introduction to deep learning

## Self-driving cars

Self-driving transportation is no longer a distant fantasy, but a reality. That's why car manufacturers, taxi aggregators, and IT companies are testing their autonomous vehicles, and some projects have already been partially implemented.

The most important aspect of autonomous driving is having a clear view of everything around: signs, roads, pedestrians, other vehicles, and other objects. If the car misunderstands the situation on the road, the cost of the mistake will be high. That's why autonomous transportation is equipped with various sensors, with cameras and lidars being the most important ones.

However, it's not enough to simply see objects - it's also necessary to understand which objects are in the field of view. For example, in a critical situation, an autonomous car should be able to distinguish between a person and a lamppost and understand road signs to avoid confusing a speed limit of 60 km/h with a "brick". That's why various computer vision algorithms are applied to understand the situation on the road.

## **Computer Vision**

The color in RGB is defined by a triplet of numbers, each of which takes a value from 0 to 255, for example, [127, 53, 65].

(https://github.com/SEAME-TEAM01/ADS01-Lane-Keeping-Assist/blob/welida42-patch-1/docs/imgs/rgb.png)
The main parameters of an image are its width and height in pixels, as well as the number of channels. The size of an uncompressed image in bytes is the product of its height, width, and number of channels.

![rgb chanels.jpg](ADS%20for%20docs%202e45af324dd34bfe9413a907c7240d3d/rgb_chanels.jpg)

Images are a set of numbers. If an image is black and white, each pixel stores a number from 0 (black) to 255 (white).

![https://pictures.s3.yandex.net/resources/log_1586169165.jpg](https://pictures.s3.yandex.net/resources/log_1586169165.jpg)

## ****Neural networks****

Neural nets are a means of doing machine learning, in which a computer learns to perform some task by analyzing training examples. Usually, the examples have been hand-labeled in advance. An object recognition system, for instance, might be fed thousands of labeled images of cars, houses, coffee cups, and so on, and it would find visual patterns in the images that consistently correlate with particular labels.

## ****Fully connected neural networks****

**Fully connected layers - l**ayers in which all inputs are connected to all neurons



Lets look on network wich consist of only one neuron or values at one output. It has *n* inputs, each multiplied by its weight. For example, *x₁* is multiplied by *w₁*. There is another input that is always equal to one. Its weight is denoted as *b* (bias). The process of training a neural network consists of adjusting the weights *w* and *b*. After all the products of input values and weights are summed, the output of the neural network (*a*) is provided.

![https://pictures.s3.yandex.net/resources/x1_1586165939.jpg](https://pictures.s3.yandex.net/resources/x1_1586165939.jpg)

**Linear regression is also a neural network, but with only one neuron!**

If there are only two classes for the objects, then the difference between linear and logistic regressions is almost imperceptible. Only one element needs to be added.

And here's how it looks - **logistic** **regression** :

![https://pictures.s3.yandex.net/resources/x1-1_1586166651.jpg](https://pictures.s3.yandex.net/resources/x1-1_1586166651.jpg)

A **sigmoid function** has been added to the schema, which is a familiar activation function for neurons. It takes any real number as input and returns a number in the range from 0 (no activation) to 1 (activation present).

[https://pictures.s3.yandex.net/resources/jpg_1586166688](https://pictures.s3.yandex.net/resources/jpg_1586166688)

This number in the range from 0 to 1 can be interpreted as a prediction of a neural network, indicating whether the object belongs to the negative or positive class.

[https://pictures.s3.yandex.net/resources/jpg_1_1586166704](https://pictures.s3.yandex.net/resources/jpg_1_1586166704)

The loss function changes depending on the type of neural network. If **Mean Squared Error (MSE)** was used in regression tasks, **Binary Cross-Entropy** is suitable for binary classification.

**BCE** is calculated as follows:

[https://pictures.s3.yandex.net/resources/jpg_1586166784](https://pictures.s3.yandex.net/resources/jpg_1586166784)

**Signal vanishing, ReLU**

With an increase in the number of layers, the quality of training deteriorates. The more layers in the network, the less signal reaches the network output. This is called signal vanishing. The reason for the vanishing signal is in the sigmoid function, which converts large values into small ones multiple times.

To eliminate signal vanishing, you can choose a different activation function. For example, ReLU (Rectified Linear Unit):

[https://pictures.s3.yandex.net/resources/jpg_1586168291](https://pictures.s3.yandex.net/resources/jpg_1586168291)

[https://pictures.s3.yandex.net/resources/jpgagg_1586168313](https://pictures.s3.yandex.net/resources/jpgagg_1586168313)

# Convolution

Fully connected networks cannot handle large images: if there are too few neurons, the network will not find dependencies, and if there are too many, it will overfit. Convolution solves this problem.

To find important elements for classification, convolution applies the same operations to all pixels.

Convolution (*c*) is performed as follows: weights (*w*) "slide" along the sequence (*s*), and a scalar product is calculated at each position.

[_2.mp4](ADS%20for%20docs%202e45af324dd34bfe9413a907c7240d3d/_2.mp4)

Now let's take a look at how two-dimensional convolution works.

We have a two-dimensional image *s* with a size of *m×m* pixels and a weight matrix *w* with a size of *n×n* pixels. This matrix is called the convolution kernel.

The kernel moves over the image from left to right and top to bottom. At each position, its weights are multiplied element-wise with the corresponding pixels. The resulting products are then summed up and recorded as the pixels of the output.

[112.mp4](ADS%20for%20docs%202e45af324dd34bfe9413a907c7240d3d/112.mp4)

Now - for examples.

With the convolution operation, it is possible to find the contours of this image:

![https://pictures.s3.yandex.net/resources/Untitled_1663692815.png](https://pictures.s3.yandex.net/resources/Untitled_1663692815.png)

Horizontal contours can be detected using a convolution with the following kernel:

```python
np.array([[-1, -2, -1],
          [ 0,  0,  0],
          [ 1,  2,  1]])
```

![https://pictures.s3.yandex.net/resources/Untitled_1_1663692838.png](https://pictures.s3.yandex.net/resources/Untitled_1_1663692838.png)

Vertical contours can be detected using a convolution with the following kernel:

```python
np.array([[-1, 0, 1],
          [-2, 0, 2],
          [-1, 0, 1]])
```

Result of convolution :

![https://pictures.s3.yandex.net/resources/Untitled_2_1663692873.png](https://pictures.s3.yandex.net/resources/Untitled_2_1663692873.png)

Contours of the image have been obtained!

The convolutional layer consists of customizable and trainable filters, which are sets of weights applied to the image. Essentially, these are square matrices of size *K×K* of pixels.

If the image is colored, the filter also includes depth, which is a third dimension. In this case, the filter is no longer a matrix but a tensor, or a multidimensional table.

Let's look at an example. You have three channels: red, blue, and green. A filter of size 3x3x3 (three pixels in width, height, and depth) sequentially moves across the input image in each channel, performing convolution operations. It does not move along the third dimension. The weights are different for different colors. The resulting images are element-wise summed to form the convolution result.

![https://pictures.s3.yandex.net/resources/_2_1586706966.gif](https://pictures.s3.yandex.net/resources/_2_1586706966.gif)

There can be several filters in a convolution layer. Each filter returns a two-dimensional image from which you can make a three-dimensional image again. On the next convolution layer, the depth of the filters is equal to the number of filters on the previous layer.

There are far fewer parameters in convolution layers than in full-connected layers. So, convolutional layers are easier to train.

To compare the number of operations in convolutional and full-link layers, consider an example. The input of a convolutional layer is an image of size 32x32x3. The filter has a size of 3x3x3. The output image is 30x30x1, i.e. with one channel. So, there are 27 parameters (3-3-3) in such a convolutional layer.

Now about the fully connected layer. If we convert a 32x32x3 image into a 30x30 image, a neuron is added to each output pixel, i.e. we need 900 neurons in total (30-30). Each neuron is associated with all pixels in the input image, that is a total of 2,764,800 parameters (32-32-3-900).

The difference in performance between the convolutional and fully connected layers is significant. For large images, the results will be even more noticeable.

### Consider the settings of the convolution layer:

1. **Padding.** This technique adds zeros (*zero padding*) to the edges of the matrix, so that the outermost pixels participate in convolution as many times as the center pixels. This way important information in the image will not be lost. Added zeros also take part in convolution. The padding value sets the thickness of the zero padding.
    
    ![image (1).jpg](ADS%20for%20docs%202e45af324dd34bfe9413a907c7240d3d/image_(1).jpg)
    
2. **Striding, or Stride.** This technique shifts the filter not by one pixel, but by a larger number of pixels. It is used when you want a smaller output image.

![https://pictures.s3.yandex.net/resources/_4_1586706987.gif](https://pictures.s3.yandex.net/resources/_4_1586706987.gif)

The output tensor size after convolution layer is calculated as follows. If the initial image size W×W×D (from English width, depth) has a filter K×K×D, padding (P) and step (S), the new image size *W' is calculated by the formula:

![https://pictures.s3.yandex.net/resources/w_1586706450.jpg](https://pictures.s3.yandex.net/resources/w_1586706450.jpg)

Example: an input image of size 7x7x3 and a 3x3x3 filter with padding 0 and step 1 will have an output tensor of size 5x5.

**Pooling** - This is a technique that reduces the number of model parameters. It can be seen in the example of Max Pooling

![3_1586707886.jpg](ADS%20for%20docs%202e45af324dd34bfe9413a907c7240d3d/3_1586707886.jpg)

**Gradient descent (*SGD*)** is not the most optimal algorithm for training a neural network. If the step size is too small, the network will take a long time to train, and if the step size is too large, it may miss the minimum. To make the step selection automatic, the **Adam** algorithm is used. **Adaptive moment estimation,* "adaptivity based on moment estimation"). It selects different parameters for different neurons, which also speeds up model training.

Full-link networks usually have no more than 2-5 layers because:- There are research papers that prove that three fully-connected layers with nonlinear activation are theoretically enough to learn anything, only in practice they do not have enough time to do so.

- If a network has many layers, it stops learning due to gradient decay.

This is not quite the case with convolutional networks:

1.They have fewer parameters than fully-connected ones, so more layers can be added to them.
2. When dealing with images, the quality of the network improves if you add convolutional layers to it.
3. In convolutional neural networks, gradient fading also occurs. Therefore, the first representatives had about 20 layers. Often a number is added to the name of the network, such as VGG16 and VGG19. 16 and 19 is just the number of layers. The new layers no longer improved the quality as the first ones hardly learned any more.

The ResNet architecture arose to solve the problem of fading gradient in very deep networks. It makes it easy to train 100 layers. There are even examples of trained networks deeper than 400 layers.

# Image Segmentation Task

In the classification task, the goal is to predict the class of the entire image, while in the detection task, it is to predict each object. And in the segmentation task, it is to predict each pixel. The result of the prediction is another image that may look like this:

![ADS%20for%20docs%202e45af324dd34bfe9413a907c7240d3d/Untitled_6_1659462322.png](ADS%20for%20docs%202e45af324dd34bfe9413a907c7240d3d/Untitled_6_1659462322.png)

Each color represents a separate class: chair, wall, ceiling, etc.

The segmentation task is divided into subtasks. If you need to assign a specific class to each pixel, then you have a semantic segmentation task. The output of a **semantic segmentation** model should be a mask - an image in which objects of the same class have the same color. However, if there are two or three sofas in the photo, they will have the same class.

In **instance segmentation** task, each pixel is assigned a specific instance of a class. In this case, two sofas would be considered as different objects. The output returns a list of objects with descriptions of their locations, assigned class, and prediction accuracy. The location of an object is described by the coordinates of its contour or mask - a binary matrix of the same size as the input image. 0 denotes the absence of an object, 1 denotes its presence.

## Quality Metrics for Segmentation

In semantic segmentation tasks, each pixel is assigned a specific class, which allows us to calculate the per-pixel accuracy. It is the ratio of pixels for which the model correctly assigns a class.

The IoU metric is also suitable for semantic segmentation. Instead of rectangles, it considers shapes bounded by contours.

In addition to IoU, the Sørensen-Dice coefficient, or **Dice coefficient**, can be used. It is the ratio of twice the intersection area to the sum of the prediction and ground truth areas.

![https://pictures.s3.yandex.net/resources/Frame_339_1_1659462353.png](https://pictures.s3.yandex.net/resources/Frame_339_1_1659462353.png)

## Object Segmentation Algorithm

The classical model for semantic segmentation is [U-Net](https://arxiv.org/abs/1505.04597).

Like many other computer vision models, U-Net is a neural network. It was developed to detect pathologies in medical images. U-Net "looks" at the image at different scales and determines the class to which each pixel belongs.

## Loss Function in Segmentation Task

The loss function in the semantic segmentation task, in the simple case, is pixel-level cross-entropy. More complex loss functions are used for instance segmentation.

The task of segmentation is to determine the class of each pixel in an image. During the process, the model creates a segmentation mask. The main architecture for the segmentation task is U-Net.

Links to useful resources:

Overview of machine learning algorithms with simple explanations, examples and visualizations:

[https://vas3k.com/blog/machine_learning/](https://vas3k.com/blog/machine_learning/)

Visualization of neural networks with different parameters:

[https://playground.tensorflow.org/](https://playground.tensorflow.org/)

The basics of neural networks, and the math behind how they learn:

[https://www.3blue1brown.com/topics/neural-networks](https://www.3blue1brown.com/topics/neural-networks)
