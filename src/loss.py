import tensorflow as tf

# loss.py
def instance_loss(instance_label, net_out, embed_size=4, img_size=(256, 512)):
    k_instance = 1.0
    k_dist = 1.0


    inst_seg = net_out
    instance_label = rgb_to_instance_ids(instance_label)
    _, var_loss, dist_loss, reg_loss = discriminative_loss(inst_seg, instance_label, embed_size, img_size)


    var_loss = var_loss * k_instance
    dist_loss = dist_loss * k_dist
    inst_loss = var_loss + dist_loss

    return inst_loss

def rgb_to_instance_ids(rgb_labels):
    instance_ids = rgb_labels[..., 0] * 65536 + rgb_labels[..., 1] * 256 + rgb_labels[..., 2]

    instance_ids = tf.expand_dims(instance_ids, -1)

    return instance_ids

def discriminative_loss_single(prediction, correct_label, feature_dim, label_shape,
                            delta_v=0.5, delta_d=3, param_var=1.0, param_dist=1.0, param_reg=0.0):

    ''' Discriminative loss for a single prediction/label pair.
    :param prediction: inference of network
    :param correct_label: instance label
    :feature_dim: feature dimension of prediction
    :param label_shape: shape of label
    :param delta_v: cutoff variance distance
    :param delta_d: curoff cluster distance
    :param param_var: weight for intra cluster variance
    :param param_dist: weight for inter cluster distances
    :param param_reg: weight regularization
    '''

    ### Reshape so pixels are aligned along a vector
    correct_label = tf.reshape(correct_label, [label_shape[1]*label_shape[0]])
    reshaped_pred = tf.reshape(prediction, [label_shape[1]*label_shape[0], feature_dim])

    correct_label = tf.cast(correct_label, dtype=tf.float32)
    reshaped_pred = tf.cast(reshaped_pred, dtype=tf.float32)
    unique_labels, unique_id, counts = tf.unique_with_counts(correct_label)
    counts = tf.cast(counts, tf.float32)
    num_instances = tf.size(unique_labels)

    segmented_sum = tf.math.unsorted_segment_sum(reshaped_pred, unique_id, num_instances)
    segmented_sum = tf.cast(segmented_sum, dtype=tf.float32)
    mu = tf.math.divide(segmented_sum, tf.reshape(counts, (-1, 1)))
    mu_expand = tf.gather(mu, unique_id)

    ### Calculate l_var
    distance = tf.subtract(mu_expand, reshaped_pred)
    distance = tf.norm(distance, axis=1)
    distance = tf.subtract(distance, delta_v)
    distance = tf.clip_by_value(distance, 0., distance)
    distance = tf.square(distance)

    l_var = tf.math.unsorted_segment_sum(distance, unique_id, num_instances)
    l_var = tf.math.divide(l_var, counts)
    l_var = tf.reduce_sum(l_var)
    l_var = tf.math.divide(l_var, tf.cast(num_instances, tf.float32))

    ### Calculate l_dist

    # Get distance for each pair of clusters like this:
    #   mu_1 - mu_1
    #   mu_2 - mu_1
    #   mu_3 - mu_1
    #   mu_1 - mu_2
    #   mu_2 - mu_2
    #   mu_3 - mu_2
    #   mu_1 - mu_3
    #   mu_2 - mu_3
    #   mu_3 - mu_3

    mu_interleaved_rep = tf.tile(mu, [num_instances, 1])
    mu_band_rep = tf.tile(mu, [1, num_instances])
    mu_band_rep = tf.reshape(mu_band_rep, (num_instances*num_instances, feature_dim))

    mu_diff = tf.subtract(mu_band_rep, mu_interleaved_rep)

    # Filter out zeros from same cluster subtraction
    intermediate_tensor = tf.reduce_sum(tf.abs(mu_diff),axis=1)
    zero_vector = tf.zeros(1, dtype=tf.float32)
    bool_mask = tf.not_equal(intermediate_tensor, zero_vector)
    mu_diff_bool = tf.boolean_mask(mu_diff, bool_mask)

    mu_norm = tf.norm(mu_diff_bool, axis=1)
    mu_norm = tf.subtract(2.*delta_d, mu_norm)
    mu_norm = tf.clip_by_value(mu_norm, 0., mu_norm)
    mu_norm = tf.square(mu_norm)

    l_dist = tf.reduce_mean(mu_norm)

    ### Calculate l_reg
    l_reg = tf.reduce_mean(tf.norm(mu, axis=1))

    param_scale = 1.
    l_var = param_var * l_var
    l_dist = param_dist * l_dist
    l_reg = param_reg * l_reg

    loss = param_scale*(l_var + l_dist + l_reg)

    return loss, l_var, l_dist, l_reg

def discriminative_loss(prediction, correct_label, feature_dim, image_shape,
                delta_v=0.5, delta_d=1.5, param_var=1.5, param_dist=1.0, param_reg=1.0):
    ''' Iterate over a batch of prediction/label and cumulate loss
    :return: discriminative loss and its three components
    '''
    def cond(label, batch, out_loss, out_var, out_dist, out_reg, i):
        return tf.math.less(i, tf.shape(batch)[0])

    def body(label, batch, out_loss, out_var, out_dist, out_reg, i):
        disc_loss, l_var, l_dist, l_reg = discriminative_loss_single(prediction[i], correct_label[i], feature_dim, image_shape,
                        delta_v, delta_d, param_var, param_dist, param_reg)

        out_loss = out_loss.write(i, disc_loss)
        out_var = out_var.write(i, l_var)
        out_dist = out_dist.write(i, l_dist)
        out_reg = out_reg.write(i, l_reg)

        return label, batch, out_loss, out_var, out_dist, out_reg, i + 1

    # TensorArray is a data structure that support dynamic writing
    output_ta_loss = tf.TensorArray(dtype=tf.float32,
                   size=0,
                   dynamic_size=True)
    output_ta_var = tf.TensorArray(dtype=tf.float32,
                   size=0,
                   dynamic_size=True)
    output_ta_dist = tf.TensorArray(dtype=tf.float32,
                   size=0,
                   dynamic_size=True)
    output_ta_reg = tf.TensorArray(dtype=tf.float32,
                   size=0,
                   dynamic_size=True)
    _, _, out_loss_op, out_var_op, out_dist_op, out_reg_op, _  = tf.while_loop(cond, body, [correct_label,
                                                        prediction,
                                                        output_ta_loss,
                                                        output_ta_var,
                                                        output_ta_dist,
                                                        output_ta_reg,
                                                        0])
    out_loss_op = out_loss_op.stack()
    out_var_op = out_var_op.stack()
    out_dist_op = out_dist_op.stack()
    out_reg_op = out_reg_op.stack()

    disc_loss = tf.reduce_mean(out_loss_op)
    l_var = tf.reduce_mean(out_var_op)
    l_dist = tf.reduce_mean(out_dist_op)
    l_reg = tf.reduce_mean(out_reg_op)

    return disc_loss, l_var, l_dist, l_reg
