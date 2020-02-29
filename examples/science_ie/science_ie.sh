#!/usr/bin/env bash


EXPERIMENT_PREFIX="lstm_crf_scienceie"
SCRIPT_FILE="science_ie.py"

python ${SCRIPT_FILE} \
--exp_name ${EXPERIMENT_PREFIX} \
--exp_dir_path  "./output" \
--model_save_dir "./output/checkpoints" \
--device cuda:2 \
--dropout 0.4 \
--reg 0 \
--bs 64 \
--emb_type "glove_6B_100" \
--char_emb_dim 50 \
--char_encoder_hidden_dim 100 \
--hidden_dim 256 \
--bidirectional \
--lr 1e-3 \
--combine_strategy concat \
--epochs 50 \
--save_every 10 \
--log_train_metrics_every 10 \
--sample_proportion 1