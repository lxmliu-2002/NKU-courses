# coding: utf-8
import numpy as np
import utils
import logging

# 配置日志
logging.basicConfig(
    filename = "log.log",
    level = logging.DEBUG,
    format = "%(asctime)s %(levelname)s:%(message)s",
)


class Trainer:
    """
    神经网络的训练器
    """

    def __init__(
        self,
        network,
        x_train,
        t_train,
        x_test,
        t_test,
        epochs = 20,
        mini_batch_size = 100,
        optimizer = "SGD",
        optimizer_param = {"lr": 0.01},
        evaluate_sample_num_per_epoch = None,
        verbose = True,
    ):
        self.network = network
        self.verbose = verbose
        self.x_train = x_train
        self.t_train = t_train
        self.x_test = x_test
        self.t_test = t_test
        self.epochs = epochs
        self.batch_size = mini_batch_size
        self.evaluate_sample_num_per_epoch = evaluate_sample_num_per_epoch

        # optimizer
        optimizer_class_dict = {
            "sgd": utils.SGD,
            "momentum": utils.Momentum,
            "adam": utils.Adam,
            "rmsprop": utils.RMSprop,
            "adagrad": utils.AdaGrad,
        }
        self.optimizer = optimizer_class_dict[optimizer.lower()](**optimizer_param)

        # 训练相关的参数
        self.train_size = x_train.shape[0]
        self.iter_per_epoch = max(self.train_size / mini_batch_size, 1)
        self.max_iter = int(epochs * self.iter_per_epoch)
        self.current_iter = 0
        self.current_epoch = 0
        # 记录每次epoch的识别精度
        self.train_loss_list = []
        self.train_acc_list = []
        self.test_acc_list = []

    def train_step(self):
        batch_mask = np.random.choice(self.train_size, self.batch_size)
        x_batch = self.x_train[batch_mask]
        t_batch = self.t_train[batch_mask]

        grads = self.network.gradient(x_batch, t_batch)
        self.optimizer.update(self.network.params, grads)

        loss = self.network.loss(x_batch, t_batch)
        self.train_loss_list.append(loss)
        if self.verbose:
            print("train loss:" + str(loss))

        # 每个epoch结束
        if self.current_iter % self.iter_per_epoch == 0:
            self.current_epoch += 1

            x_train_sample, t_train_sample = self.x_train, self.t_train
            x_test_sample, t_test_sample = self.x_test, self.t_test
            # 如果有指定每个epoch的样本数，则从训练集中随机抽取指定数目的样本进行评估
            if not self.evaluate_sample_num_per_epoch is None:
                t = self.evaluate_sample_num_per_epoch
                x_train_sample, t_train_sample = self.x_train[:t], self.t_train[:t]
                x_test_sample, t_test_sample = self.x_test[:t], self.t_test[:t]
            # 计算训练集和测试集的识别精度
            train_acc = self.network.accuracy(x_train_sample, t_train_sample)
            test_acc = self.network.accuracy(x_test_sample, t_test_sample)
            self.train_acc_list.append(train_acc)
            self.test_acc_list.append(test_acc)
            # 输出
            if self.verbose:
                logging.info(
                    "=== epoch:"
                    + str(self.current_epoch)
                    + ", train acc:"
                    + str(train_acc)
                    + ", test acc:"
                    + str(test_acc)
                    + " ==="
                )
                print(
                    "=== epoch:"
                    + str(self.current_epoch)
                    + ", train acc:"
                    + str(train_acc)
                    + ", test acc:"
                    + str(test_acc)
                    + " ==="
                )
        self.current_iter += 1

    def train(self):
        for i in range(self.max_iter):
            self.train_step()
        # 测试集上的识别精度
        test_acc = self.network.accuracy(self.x_test, self.t_test)

        if self.verbose:
            logging.info("=============== Final Test Accuracy ===============")
            logging.info("test acc:" + str(test_acc))
            print("=============== Final Test Accuracy ===============")
            print("test acc:" + str(test_acc))
