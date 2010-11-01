// module for interlocks on the email settings form.
jQuery.noConflict();
GSEmailSettingsInterlock = function () {
    // Private methods
    var deliveryChange = function () {
        var updatedWidget = jQuery(this);
        var allDestinationCheckboxes = jQuery("input[name=form\\.destination]:checkbox");
        var allDefaultOrSpecificRadios = jQuery("input[name=form\\.default_or_specific]:radio");
        var checkedDefaultOrSpecificRadios = jQuery("input[name=form\\.default_or_specific]:checked");
        var destinationWidget = jQuery("#widget-form\\.destination");
        var defaultOrSpecificWidget = jQuery("#widget-form\\.default_or_specific");
        var checkedValue = updatedWidget.attr("checked");

        // check what was selected
        if (checkedValue == true && updatedWidget.attr("value") == 'web') {
            destinationWidget.hide();
            defaultOrSpecificWidget.hide();
            // allDestinationCheckboxes.attr("disabled", true);
            // allDefaultOrSpecificRadios.attr("disabled", true);
        }
        else if (checkedValue == true) {
            if (checkedDefaultOrSpecificRadios.attr("value") == "specific") {
                destinationWidget.show();
            }
            defaultOrSpecificWidget.show();
            allDestinationCheckboxes.attr("disabled", false);
            allDefaultOrSpecificRadios.attr("disabled", false);
        }
    }
    
    var defaultOrSpecificChange = function () {
        var updatedWidget = jQuery(this);
        var allDestinationCheckboxes = jQuery("input[name=form\\.destination]:checkbox");
        var checkedValue = updatedWidget.attr("checked");
        var destinationWidget = jQuery("#widget-form\\.destination");

        // check what was selected
        if (checkedValue == true && updatedWidget.attr("value") == 'default') {
            destinationWidget.hide();
            allDestinationCheckboxes.attr("disabled", true);
        }
        else if (checkedValue == true && updatedWidget.attr("value") == 'specific') {
            destinationWidget.show();
            allDestinationCheckboxes.attr("disabled", false);
        }
    }
    
    var initialSettings = function () {
        var checkedDefaultOrSpecificRadios = jQuery("input[name=form\\.default_or_specific]:checked");
        var checkedDeliveryRadios = jQuery("input[name=form\\.delivery]:checked");
        var destinationWidget = jQuery("#widget-form\\.destination");
        var defaultOrSpecificWidget = jQuery("#widget-form\\.default_or_specific");
        
        if (checkedDefaultOrSpecificRadios.attr("value") == "default") {
            destinationWidget.hide();
        }
        
        if (checkedDeliveryRadios.attr("value") == "web") {
            defaultOrSpecificWidget.hide();
            destinationWidget.hide();
        }
    }
    
    // Public methods and properties
    return {
        init: function () {
    		initialSettings();
            jQuery("input[name=form\\.default_or_specific]:radio").change(defaultOrSpecificChange);
            jQuery("input[name=form\\.delivery]:radio").change(deliveryChange);
        }
    };
}();
