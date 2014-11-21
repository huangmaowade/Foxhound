import theano
import theano.tensor as T
import numpy as np

def clip_norm(g, n):
	if n > 0:
		norm = T.sqrt(T.sum(T.sqr(g)))
		desired = T.clip(norm, 0, n)
		g = g * (desired/ (1e-7 + norm))
	return g

def clip_norms(gs, n):
	return [clip_norm(g, n) for g in gs]


class Regularizer(object):

	def __init__(self, l1=0., l2=0., maxnorm=0.):
		self.__dict__.update(locals())

	def max_norm(self, p, maxnorm):
		if maxnorm > 0:
			norms = T.sqrt(T.sum(T.sqr(p), axis=0))
			desired = T.clip(norms, 0, maxnorm)
			p = p * (desired/ (1e-7 + norms))
		return p

	def regularize(self, p):
		p = self.max_norm(p, self.maxnorm)
		p -= p * self.l2
		p -= self.l1
		return p


class Update(object):

	def __init__(self, regularizer=Regularizer(), clipnorm=0.):
		self.__dict__.update(locals())

	def get_updates(self, params, grads):
		raise NotImplementedError


class SGD(Update):

	def __init__(self, lr=0.01, *args, **kwargs):
		Update.__init__(self, *args, **kwargs)
		self.__dict__.update(locals())

	def get_updates(self, params, cost):
		updates = []
		grads = T.grad(cost, params)
		grads = clip_norms(grads, self.clipnorm)
		for p,g in zip(params,grads):
			updated_p = p - self.lr * g
			updated_p = self.regularizer.regularize(updated_p)
			updates.append((p, updated_p))
		return updates


class Momentum(Update):

	def __init__(self, lr=0.01, momentum=0.9, *args, **kwargs):
		Update.__init__(self, *args, **kwargs)
		self.__dict__.update(locals())

	def get_updates(self, params, cost):
		updates = []
		grads = T.grad(cost, params)
		grads = clip_norms(grads, self.clipnorm)
		for p,g in zip(params,grads):
			m = theano.shared(p.get_value() * 0.)
			v = (self.momentum * m) - (self.lr * g)
			updates.append((m, v))

			updated_p = p + v
			updated_p = self.regularizer.regularize(updated_p)
			updates.append((p, updated_p))
		return updates


class NAG(Update):

	def __init__(self, lr=0.01, momentum=0.9, *args, **kwargs):
		Update.__init__(self, *args, **kwargs)
		self.__dict__.update(locals())

	def get_updates(self, params, cost):
		updates = []
		grads = T.grad(cost, params)
		grads = clip_norms(grads, self.clipnorm)
		for p,g in zip(params,grads):
			m = theano.shared(p.get_value() * 0.)
			v = (self.momentum * m) - (self.lr * g)
			updates.append((m,v))

			updated_p = p + self.momentum * v - self.lr * g
			updated_p = self.regularizer.regularize(updated_p)
			updates.append((p, updated_p))
		return updates


class RMSprop(Update):

	def __init__(self, lr=0.001, rho=0.9, epsilon=1e-6, *args, **kwargs):
		Update.__init__(self, *args, **kwargs)
		self.__dict__.update(locals())

	def get_updates(self, params, cost):
		updates = []
		grads = T.grad(cost, params)
		grads = clip_norms(grads, self.clipnorm)
		for p,g in zip(params,grads):
			acc = theano.shared(p.get_value() * 0.)
			acc_new = self.rho * acc + (1 - self.rho) * g ** 2
			updates.append((acc, acc_new))

			updated_p = p - self.lr * (g / T.sqrt(acc_new + self.epsilon))
			updated_p = self.regularizer.regularize(updated_p)
			updates.append((p, updated_p))
		return updates


class Adagrad(Update):

	def __init__(self, lr=0.01, epsilon=1e-6, *args, **kwargs):
		Update.__init__(self, *args, **kwargs)
		self.__dict__.update(locals())

	def get_updates(self, params, cost):
		updates = []
		grads = T.grad(cost, params)
		grads = clip_norms(grads, self.clipnorm)
		for p,g in zip(params,grads):
			acc = theano.shared(p.get_value() * 0.)
			acc_new += g ** 2
			updates.append((acc, acc_new))

			updated_p = p - (self.lr / T.sqrt(acc_new + self.epsilon)) * g
			updated_p = self.regularizer.regularize(updated_p)
			updates.append((p, updated_p))
		return updates	


class Adadelta(Update):

	def __init__(self, lr=1., rho=0.95, epsilon=1e-6, *args, **kwargs):
		Update.__init__(self, *args, **kwargs)
		self.__dict__.update(locals())

	def get_updates(self, params, cost):
		updates = []
		grads = T.grad(cost, params)
		grads = clip_norms(grads, self.clipnorm)
		for p,g in zip(params,grads):
			acc = theano.shared(p.get_value() * 0.)
			acc_delta = theano.shared(p.get_value() * 0.)
			acc_new = self.rho * acc + (1 - self.rho) * g ** 2
			updates.append((acc,acc_new))

			update = g * T.sqrt(acc_delta + self.epsilon) / T.sqrt(acc_new + self.epsilon)
			updated_p = p - self.lr * update
			updated_p = self.regularizer.regularize(updated_p)
			updates.append((p, updated_p))

			acc_delta_new = self.rho * acc_delta + (1 - self.rho) * update ** 2
			updates.append((acc_delta,acc_delta_new))
		return updates
