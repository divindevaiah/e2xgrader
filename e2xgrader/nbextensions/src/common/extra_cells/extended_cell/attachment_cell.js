define([
    'jquery',
    './extended_cell',
    './attachment_view'
], function (
    $,
    extended_cell,
    attachment_view
) {

    'use strict';

    let ExtendedCell = extended_cell.ExtendedCell;

    class AttachmentCell extends ExtendedCell {

        constructor(cell) {            
            super(cell, 'attachments');
            this.model = new attachment_view.AttachmentModel(cell);
            this.view = new attachment_view.AttachmentGallery(cell, this.model);
        }

        get_attachment_button() {
            let that = this;
            return $('<button>')
                .attr('type', 'button')
                .addClass('edit_attachments')
                .click(function () {
                    that.view.open();
                }).append('Add Files / Images');
        }

        render = function() {
            this.cell.render_force();
            let html = $(this.cell.element).find('.rendered_html');
            if (html.find('.edit_attachments').length < 1) {
                html.append(this.get_attachment_button());
            }
            this.add_edit_button();
        }

    }

    return {
        AttachmentCell: AttachmentCell,
    };

});