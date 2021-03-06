/**
 * The new upgraded Searchfield doesn't work for us. It broke in multiple places
 * such as custom layer or even searches in known layer registered layer.
 * We have resorted to use the old SearchField and override the 4.1.1 version.
 */
Ext.define('Ext.ux.form.SearchField', {
    extend: 'Ext.form.field.Trigger',

    alias: 'widget.searchfield',

    trigger1Cls: Ext.baseCSSPrefix + 'form-clear-trigger',

    trigger2Cls: Ext.baseCSSPrefix + 'form-search-trigger',

    hasSearch : false,
    paramName : 'query',

    initComponent: function(){
        this.callParent(arguments);
        this.on('specialkey', function(f, e){
            if(e.getKey() == e.ENTER){
                this.onTrigger2Click();
            }
        }, this);
    },

    afterRender: function(){
        this.callParent();
        this.triggerCell.item(0).setDisplayed(false);
    },

    onTrigger1Click : function(){
        var me = this,
            store = me.store,
            proxy = store.getProxy(),
            val;

        if (me.hasSearch) {
            me.setValue('');
            proxy.extraParams[me.paramName] = '';
            this._clearLayerStore(store);            
            me.hasSearch = false;
            me.triggerCell.item(0).setDisplayed(false);
            me.doComponentLayout();
        }
    },
    
    _clearLayerStore : function(store){
        store.query("active",true).each(function(record){
            record.get('layer').removeDataFromMap();
        })
        store.removeAll();
    },

    onTrigger2Click : function(){
        var me = this,
            store = me.store,
            proxy = store.getProxy(),
            value = me.getValue();

        if (value.length < 1) {
            me.onTrigger1Click();
            return;
        }
        proxy.extraParams[me.paramName] = value;
        store.loadPage(1);
        me.hasSearch = true;
        me.triggerCell.item(0).setDisplayed(true);
        me.doComponentLayout();
    }
});