from typing import Union, Dict, List, Any, Optional
from parsect.utils.common import convert_generic_sect_to_json
import wasabi
from parsect.tokenizers.word_tokenizer import WordTokenizer
from parsect.vocab.vocab import Vocab
from parsect.numericalizer.numericalizer import Numericalizer
from parsect.utils.common import pack_to_length
import torch
from parsect.datasets.classification.base_text_classification import (
    BaseTextClassification,
)
from parsect.datasets.sprinkle_dataset import sprinkle_dataset
from parsect.utils.class_nursery import ClassNursery


@sprinkle_dataset()
class GenericSectDataset(BaseTextClassification, ClassNursery):
    def __init__(
        self,
        filename: str,
        dataset_type: str,
        max_num_words: int,
        max_instance_length: int,
        word_vocab_store_location: str,
        debug: bool = False,
        debug_dataset_proportion: float = 0.1,
        word_embedding_type: Union[str, None] = None,
        word_embedding_dimension: Union[int, None] = None,
        word_start_token: str = "<SOS>",
        word_end_token: str = "<EOS>",
        word_pad_token: str = "<PAD>",
        word_unk_token: str = "<UNK>",
        train_size: float = 0.8,
        test_size: float = 0.2,
        validation_size: float = 0.5,
        word_tokenizer=WordTokenizer(),
        word_tokenization_type="vanilla",
        add_start_end_token: bool = True,
    ):
        self.classname2idx = self.get_classname2idx()
        self.idx2classname = {
            idx: classname for classname, idx in self.classname2idx.items()
        }
        self.filename = filename
        self.train_size = train_size
        self.test_size = test_size
        self.validation_size = validation_size
        self.dataset_type = dataset_type
        self.debug = debug
        self.debug_dataset_proportion = debug_dataset_proportion
        self.max_instance_length = max_instance_length
        self.lines, self.labels = self.get_lines_labels(filename=self.filename)

        self.msg_printer = wasabi.Printer()

    def __len__(self):
        return len(self.word_instances)

    def __getitem__(self, idx: int) -> Dict[str, Any]:
        line = self.lines[idx]
        label = self.labels[idx]

        return self.get_iter_dict(
            lines=line,
            word_vocab=self.word_vocab,
            word_tokenizer=self.word_tokenizer,
            max_word_length=self.max_instance_length,
            word_add_start_end_token=True,
            labels=label,
        )

    def get_lines_labels(self, filename: str) -> (List[str], List[str]):
        generic_sect_json = convert_generic_sect_to_json(filename=filename)
        headers = []
        labels = []

        generic_sect_json = generic_sect_json["generic_sect"]
        for line in generic_sect_json:
            label = line["label"]
            header = line["header"]
            label = label.strip()
            header = header.strip()
            headers.append(header)
            labels.append(label)

        (train_headers, train_labels), (valid_headers, valid_labels), (
            test_headers,
            test_labels,
        ) = self.get_train_valid_test_stratified_split(
            headers, labels, self.classname2idx
        )

        if self.dataset_type == "train":
            return train_headers, train_labels
        elif self.dataset_type == "valid":
            return valid_headers, valid_labels
        elif self.dataset_type == "test":
            return test_headers, test_labels

    @classmethod
    def get_classname2idx(cls) -> Dict[str, int]:
        categories = [
            "abstract",
            "categories-and-subject-descriptors",
            "general-terms",
            "introduction",
            "background",
            "related-works",
            "method",
            "evaluation",
            "discussions",
            "conclusions",
            "acknowledgments",
            "references",
        ]

        categories = [(category, idx) for idx, category in enumerate(categories)]
        categories = dict(categories)
        return categories

    def print_stats(self):
        """ Return some stats about the dataset
        """
        num_instances = self.num_instances
        formatted = self.label_stats_table
        self.msg_printer.divider("Stats for {0} dataset".format(self.dataset_type))
        print(formatted)
        self.msg_printer.info(
            f"Number of instances in {self.dataset_type} dataset - {num_instances}"
        )

    def get_num_classes(self):
        return len(self.classname2idx.keys())

    def get_class_names_from_indices(self, indices: List):
        return [self.idx2classname[idx] for idx in indices]

    @classmethod
    def emits_keys(cls) -> Dict[str, str]:
        return {
            "tokens": f"A torch.LongTensor of size `max_length`. "
            f"Example [0, 0, 1, 100] where every number represents an index in the vocab",
            "len_tokens": f"A torch.LongTensor. "
            f"Example [2] representing the number of tokens without padding",
            "label": f"A torch.LongTensor representing the label corresponding to the "
            f"instance. Example [2] representing class 2",
            "instance": f"A string that is padded to ``max_length``.",
            "raw_instance": f"A string that is not padded",
        }

    @classmethod
    def get_iter_dict(
        cls,
        lines: Union[List[str], str],
        word_vocab: Vocab,
        word_tokenizer: WordTokenizer,
        max_word_length: int,
        word_add_start_end_token: bool,
        labels: Optional[Union[str, List[str]]] = None,
    ):
        if isinstance(lines, str):
            lines = [lines]

        word_instances = word_tokenizer.tokenize_batch(lines)
        len_instances = [len(instance) for instance in word_instances]
        word_numericalizer = Numericalizer(vocabulary=word_vocab)
        classnames2idx = GenericSectDataset.get_classname2idx()

        if labels is not None:
            if isinstance(labels, str):
                labels = [labels]

            labels = [classnames2idx[label] for label in labels]
            label = torch.LongTensor(labels)

        padded_instances = []
        for word_instance in word_instances:
            padded_instance = pack_to_length(
                tokenized_text=word_instance,
                max_length=max_word_length,
                pad_token=word_vocab.pad_token,
                add_start_end_token=True,  # TODO: remove hard coded value here
                start_token=word_vocab.start_token,
                end_token=word_vocab.end_token,
            )
            padded_instances.append(padded_instance)

        tokens = word_numericalizer.numericalize_batch_instances(padded_instances)
        tokens = torch.LongTensor(tokens)
        tokens = tokens.squeeze(0)

        instances = []
        for instance in padded_instances:
            instances.append(" ".join(instance))

        raw_instances = []
        for instance in word_instances:
            raw_instances.append(" ".join(instance))

        len_tokens = torch.LongTensor(len_instances)

        # squeeze the dimensions if there are more than one dimension

        if len(instances) == 1:
            instances = instances[0]
            raw_instances = raw_instances[0]

        instance_dict = {
            "tokens": tokens,
            "len_tokens": len_tokens,
            "instance": instances,
            "raw_instance": raw_instances,
        }

        if labels is not None:
            instance_dict["label"] = label

        return instance_dict
