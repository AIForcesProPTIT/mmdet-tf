from abc import ABCMeta, abstractmethod
import tensorflow as tf


class BaseDenseHead(tf.keras.layers.Layer):
    def __init__(self,*args,**kwargs):
        super().__init__()
        if 'assigner_target_on_dataset' in kwargs:
            self.assigner_target_on_dataset = kwargs['assigner_target_on_dataset']
    def get_config(self):
        cfg = super().get_config()
        cfg['assigner_target_on_dataset'] =self.assigner_target_on_dataset
        return cfg
    def call(self, inputs, training=False):
        tf.print('call base head is not stable')
        pass
    def forward_single(self, input, training=False):
        pass
    def get_loss_affter_call(self, outputs, labels):
        pass
    def forward_train(self,
                      x,
                      gt_bboxes,
                      gt_labels=None,
                      batch_size=None,
                      proposal_cfg=None,
                      ):
        """
        Args:
            x (list[Tensor]): Features from FPN.
            img_metas (list[dict]): Meta information of each image, e.g.,
                image size, scaling factor, etc.
            gt_bboxes (Tensor): Ground truth bboxes of the image,
                shape (num_gts, 4).
            gt_labels (Tensor): Ground truth labels of each box,
                shape (num_gts,).
            gt_bboxes_ignore (Tensor): Ground truth bboxes to be
                ignored, shape (num_ignored_gts, 4).
            proposal_cfg (mmcv.Config): Test / postprocessing configuration,
                if None, test_cfg would be used
        Returns:
            tuple:
                losses: (dict[str, Tensor]): A dictionary of loss components.
                proposal_list (list[Tensor]): Proposals of each image.
        """
        outs = self(x, training=True)
        if batch_size is not None:
            gt_bboxes = tf.unstack(gt_bboxes,batch_size)
            if gt_labels is not None:
                gt_labels=tf.unstack(gt_labels, batch_size)
        if gt_labels is None:
            loss_inputs = outs + (gt_bboxes,)
        else:
            loss_inputs = outs + (gt_bboxes, gt_labels, )
        losses = self.mloss(*loss_inputs)
        if proposal_cfg is None:
            return losses
        else:
            proposal_list = self.get_bboxes(*outs,  cfg=proposal_cfg)
        return losses, proposal_list 