import theano
import theano.tensor as T

def categorical_crossentropy(target, pred):
	return T.nnet.categorical_crossentropy(pred, target).mean()

def binary_crossentropy(target, pred):
	return T.nnet.binary_crossentropy(pred, target).mean()

def mean_squared_error(target, pred):
	return T.sqr(pred - target).mean()

def mean_absolute_error(target, pred):
    return T.abs_(pred - target).mean()

# aliasing
CCE = categorical_crossentropy
BCE = binary_crossentropy
MSE = mean_squared_error
MAE = mean_absolute_error