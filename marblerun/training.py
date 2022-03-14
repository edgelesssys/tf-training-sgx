
import argparse
import json
import os
import tensorflow as tf
from tensorflow.keras import layers, models
import multiprocessing
from time import sleep


def build_and_compile_cnn_model():
    model = models.Sequential()
    model.add(
        layers.Conv2D(2, (3, 3), activation='relu', input_shape=(128, 128, 1)))
    model.add(layers.MaxPooling2D((2, 2)))
    model.add(layers.Conv2D(2, (3, 3), activation='relu'))
    model.add(layers.MaxPooling2D((2, 2)))
    model.add(layers.Conv2D(2, (3, 3), activation='relu'))
    model.add(layers.Flatten())
    model.add(layers.Dense(20, activation='relu'))
    model.add(layers.Dense(10, activation='softmax'))

    model.summary()

    model.compile(optimizer='adam',
                  loss='sparse_categorical_crossentropy',
                  metrics=['accuracy'])

    return model


def dataset_fn(input_context):
    global_batch_size = 64
    batch_size = input_context.get_per_replica_batch_size(global_batch_size)

    x = tf.random.uniform((10, 128, 128))
    y = tf.random.uniform((10,))

    dataset = tf.data.Dataset.from_tensor_slices((x, y)).shuffle(10).repeat()
    dataset = dataset.shard(
        input_context.num_input_pipelines,
        input_context.input_pipeline_id)
    dataset = dataset.batch(batch_size)
    dataset = dataset.prefetch(2)

    return dataset


def start_tf_server(cluster_resolver):
    # https://www.tensorflow.org/tutorials/distribute/parameter_server_training#if_you_use_the_same_binary_for_all_tasks
    # Set the environment variable to allow reporting worker and ps failure to the
    # coordinator. This is a workaround and won't be necessary in the future.

    num_workers = 1  # TODO #FIXME and make me depending on cluster config
    worker_config = tf.compat.v1.ConfigProto()
    if multiprocessing.cpu_count() < num_workers + 1:
        worker_config.inter_op_parallelism_threads = num_workers + 1

    server = tf.distribute.Server(
        cluster_resolver.cluster_spec(),
        job_name=cluster_resolver.task_type,
        task_index=cluster_resolver.task_id,
        protocol=cluster_resolver.rpc_layer or "grpc",
        start=True)
    server.join()


def start_coordinator(cluster_resolver, args):

    os.environ["GRPC_FAIL_FAST"] = "use_caller"

    tf_config = json.loads(os.environ.get('TF_CONFIG') or '{}')
    TASK_INDEX = tf_config['task']['index']
    NUM_PS = len(tf_config['cluster']['ps'])

    print('waiting to start server')
    sleep(30)  # Sleep for 30 seconds to give the worker pods time to start
    print('starting server')

    print('preparing parameters')
    variable_partitioner = (
        tf.distribute.experimental.partitioners.MinSizePartitioner(
            min_shard_bytes=(256 << 10),
            max_shards=NUM_PS))

    print('\ncreating parameter server strategy\n')
    strategy = tf.distribute.experimental.ParameterServerStrategy(
        cluster_resolver=cluster_resolver,
        variable_partitioner=variable_partitioner)

    print('\ncreating dataset\n')
    dc = tf.keras.utils.experimental.DatasetCreator(dataset_fn)

    print('\nbuilding model\n')
    with strategy.scope():
        model = build_and_compile_cnn_model()

    checkpoint_dir = args.checkpoint_dir
    checkpoint_prefix = os.path.join(checkpoint_dir, "ckpt_{epoch}")

    print('\nstarting training\n')
    model.fit(dc, epochs=30, steps_per_epoch=5)  # , callbacks=callbacks)


def main(parsed_args):

    os.environ['NCCL_DEBUG'] = 'INFO'

    # https://www.tensorflow.org/tutorials/distribute/parameter_server_training#real_clusters
    cluster_resolver = tf.distribute.cluster_resolver.TFConfigClusterResolver()
    if cluster_resolver.task_type in ("worker", "ps"):
        start_tf_server(cluster_resolver)
    elif cluster_resolver.task_type == "evaluator":
        # Run side-car evaluation
        pass
    else:
        # Run the coordinator.
        start_coordinator(cluster_resolver, parsed_args)


if __name__ == '__main__':

    parser = argparse.ArgumentParser()
    parser.add_argument('--log_dir',
                        type=str,
                        default='train/log',
                        help='Tensorboard log dir.')

    parser.add_argument('--checkpoint_dir',
                        type=str,
                        default='train/checkpoint',
                        help='Tensorflow checkpoint directory.')

    parsed_args = parser.parse_args()

    main(parsed_args)
