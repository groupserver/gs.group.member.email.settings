"use strict";
// module for interlocks on the email settings form.
jQuery.noConflict();

function GSEmailSettingsInterlock() {
    var allDestinationCheckboxes=null, allDefaultOrSpecificRadios=null, 
        checkedDefaultOrSpecificRadios=null, destinationWidget=null,
        defaultOrSpecificWidget=null;

    // Private methods
    function deliveryChange() {
        var updatedWidget=null, v=null;

        updatedWidget = jQuery(this);

        // check what was selected
        if ( updatedWidget.attr("value") == 'web' ) {
            destinationWidget.hide();
            defaultOrSpecificWidget.hide();
            // allDestinationCheckboxes.attr("disabled", true);
            // allDefaultOrSpecificRadios.attr("disabled", true);
        }
        else {  // Digest or One Email Per Post.
            defaultOrSpecificWidget.show();
            v = checkedDefaultOrSpecificRadios.attr("value");
            if (v == "specific") {
                destinationWidget.show();
            }
            allDestinationCheckboxes.attr("disabled", false);
            allDefaultOrSpecificRadios.attr("disabled", false);
        }
    }
    function defaultOrSpecificChange() {
        var updatedWidget=null, destinationWidget=null;

        updatedWidget = jQuery(this);
        destinationWidget = jQuery("#widget-form\\.destination");

        // check what was selected
        if (updatedWidget.attr("value") == 'default') {
            destinationWidget.hide();
            allDestinationCheckboxes.attr("disabled", true);
        }
        else if (updatedWidget.attr("value") == 'specific') {
            destinationWidget.show();
            allDestinationCheckboxes.attr("disabled", false);
        }
        checkedDefaultOrSpecificRadios = jQuery("input[name=form\\.default_or_specific]:checked");
    }
    
    function initialSettings() {
        allDestinationCheckboxes = jQuery("input[name=form\\.destination]:checkbox");
        allDefaultOrSpecificRadios = jQuery("input[name=form\\.default_or_specific]:radio");
        checkedDefaultOrSpecificRadios = jQuery("input[name=form\\.default_or_specific]:checked");
        destinationWidget = jQuery("#widget-form\\.destination");
        defaultOrSpecificWidget = jQuery("#widget-form\\.default_or_specific");
    }
    initialSettings();  // Note the automatic execution
    
    // Public methods and properties
    return {
        init: function () {
            var radios=null, checkedDeliveryRadios=null;

            allDefaultOrSpecificRadios.change(defaultOrSpecificChange);

            radios = jQuery("input[name=form\\.delivery]:radio");
            radios.change(deliveryChange);

            checkedDeliveryRadios = jQuery("input[name=form\\.delivery]:checked");
            if (checkedDefaultOrSpecificRadios.attr("value") == "default") {
                destinationWidget.hide();
            }
            
            if (checkedDeliveryRadios.attr("value") == "web") {
                defaultOrSpecificWidget.hide();
                destinationWidget.hide();
            }
        }
    };
}

jQuery(window).load( function () {
    var i=null;
    i = GSEmailSettingsInterlock();
    i.init();    
});
