import torch.nn as nn
from sciwing.modules.embedders.bow_elmo_embedder import BowElmoEmbedder
from torch.nn import CrossEntropyLoss
from torch.nn.functional import softmax
import wasabi
from typing import Dict, Any
import torch


class BowElmoLinearClassifier(nn.Module):
    def __init__(
        self,
        encoder: BowElmoEmbedder,
        encoding_dim: int,
        num_classes: int,
        classification_layer_bias: bool = True,
    ):
        super(BowElmoLinearClassifier, self).__init__()
        self.encoder = encoder
        self.encoding_dim = encoding_dim
        self.num_classes = num_classes
        self.classification_layer_bias = classification_layer_bias

        self.classification_layer = nn.Linear(
            encoding_dim, num_classes, bias=self.classification_layer_bias
        )
        self._loss = CrossEntropyLoss()
        self.msg_printer = wasabi.Printer()

    def forward(
        self,
        iter_dict: Dict[str, Any],
        is_training: bool,
        is_validation: bool,
        is_test: bool,
    ) -> Dict[str, Any]:

        x = iter_dict["instance"]
        x = [instance.split() for instance in x]

        encoding = self.encoder(x)

        # TODO: quick fix for cuda situation
        # ideally have to test by converting the instance to cuda

        encoding = encoding.cuda() if torch.cuda.is_available() else encoding

        # N * C
        # N - batch size
        # C - number of classes
        logits = self.classification_layer(encoding)

        # N * C
        # N - batch size
        # C - number of classes
        # The normalized probabilities of classification
        normalized_probs = softmax(logits, dim=1)

        output_dict = {"logits": logits, "normalized_probs": normalized_probs}

        if is_training or is_validation:
            labels = iter_dict["label"]
            labels = labels.squeeze(1)
            assert labels.ndimension() == 1, self.msg_printer.fail(
                "the labels should have 1 dimension "
                "your input has shape {0}".format(labels.size())
            )
            loss = self._loss(logits, labels)
            output_dict["loss"] = loss

        return output_dict