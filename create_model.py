from firebase import firebase
import tensorflow.compat.v1 as tf
import pandas as pd
import numpy as np
import csv

tf.disable_v2_behavior()
tf.enable_resource_variables()


firebase = firebase.FirebaseApplication("https://mhacks-13-project.firebaseio.com/")

result = firebase.get('/users', None)


# Set up, populate matrix.
# Rows = users (learners).
# Columns = users (teachers).

num_users = len(result)
uid_list = []

for uid, _ in result.items():
	uid_list.append(uid)

with open('uid.csv', 'w') as uid_file:
	wr = csv.writer(uid_file, quoting=csv.QUOTE_ALL)
	wr.writerow(uid_list)

value_matrix = [[0.0, 0.0, 0.0, 0.0], [0.0, 0.6, 0.8, 1.0], \
				[0.0, 0.0, 0.6, 0.8], [0.0, 0.0, 0.0, 0.6]]

l_t_matrix = pd.DataFrame(0.0, index=np.arange(num_users), columns=np.arange(num_users))
max_val = 0.0
# non_zero = 0


for i in range(len(uid_list)):
	for j in range(len(uid_list)):
		learner_info = result[uid_list[i]]
		teacher_info = result[uid_list[j]]

		if "Interests" in learner_info and "Skills" in teacher_info:
			val_lt = 0.0
			for interest in learner_info["Interests"]:
				if interest in teacher_info["Skills"]:
					val_lt += value_matrix[learner_info["Interests"][interest]]\
										  [teacher_info["Skills"][interest]]
			l_t_matrix.at[i, j] = val_lt

			if val_lt > max_val:
				max_val = val_lt
			# if val_lt > 0.0:
			# 	non_zero += 1

if max_val != 0.0:
	l_t_matrix = l_t_matrix / max_val  # normalize
l_t_matrix = l_t_matrix.astype("float32")

with open('max.txt', 'w') as max_file:
	max_file.write(str(max_val))

#print(l_t_matrix)
#print(max_val)
#print(non_zero)


# Build model.

num_input = num_users
num_hidden_1 = 10
num_hidden_2 = 5

X = tf.placeholder(tf.float32, [None, num_input], name="myInput")

weights = {
    'encoder_h1': tf.Variable(tf.random_normal([num_input, num_hidden_1], dtype=tf.float32)),
    'encoder_h2': tf.Variable(tf.random_normal([num_hidden_1, num_hidden_2], dtype=tf.float32)),
    'decoder_h1': tf.Variable(tf.random_normal([num_hidden_2, num_hidden_1], dtype=tf.float32)),
    'decoder_h2': tf.Variable(tf.random_normal([num_hidden_1, num_input], dtype=tf.float32)),
}

biases = {
    'encoder_b1': tf.Variable(tf.random_normal([num_hidden_1], dtype=tf.float32)),
    'encoder_b2': tf.Variable(tf.random_normal([num_hidden_2], dtype=tf.float32)),
    'decoder_b1': tf.Variable(tf.random_normal([num_hidden_1], dtype=tf.float32)),
    'decoder_b2': tf.Variable(tf.random_normal([num_input], dtype=tf.float32)),
}


def encoder(x):
    layer_1 = tf.nn.sigmoid(tf.add(tf.matmul(x, weights['encoder_h1']), biases['encoder_b1']))
    layer_2 = tf.nn.sigmoid(tf.add(tf.matmul(layer_1, weights['encoder_h2']), biases['encoder_b2']))
    return layer_2

def decoder(x):
    layer_1 = tf.nn.sigmoid(tf.add(tf.matmul(x, weights['decoder_h1']), biases['decoder_b1']))
    layer_2 = tf.nn.sigmoid(tf.add(tf.matmul(layer_1, weights['decoder_h2']), biases['decoder_b2']))
    return layer_2

encoder_op = encoder(X)
decoder_op = decoder(encoder_op)

y_pred = decoder_op
y_true = X

loss = tf.losses.mean_squared_error(y_true, y_pred)
optimizer = tf.train.RMSPropOptimizer(0.03).minimize(loss)
eval_x = tf.placeholder(tf.int32, )
eval_y = tf.placeholder(tf.int32, )
pre, pre_op = tf.metrics.precision(labels=eval_x, predictions=eval_y)

init = tf.global_variables_initializer()
local_init = tf.local_variables_initializer()
pred_data = pd.DataFrame()


# Train model.

with tf.Session() as session:
	epochs = 100
	batch_size = 25

	session.run(init)
	session.run(local_init)

	num_batches = int(l_t_matrix.shape[0] / batch_size)
	l_t_matrix = np.array_split(l_t_matrix, num_batches)

	for i in range(epochs):
		avg_cost = 0
		for batch in l_t_matrix:
			_, l = session.run([optimizer, loss], feed_dict={X: batch})
			avg_cost += l
		avg_cost /= num_batches

		print("epoch: {} Loss: {}".format(i + 1, avg_cost))

	l_t_matrix = np.concatenate(l_t_matrix, axis=0)

	preds = session.run(decoder_op, feed_dict={X: l_t_matrix})
	preds_copy = tf.identity(preds, name="myOutput")

	tf.saved_model.simple_save(session, 'model', inputs={"myInput": X}, outputs={"myOutput":preds_copy})

	preds = pd.DataFrame(preds)
	preds.to_csv('lt_matrix.csv', index=False, header=False)