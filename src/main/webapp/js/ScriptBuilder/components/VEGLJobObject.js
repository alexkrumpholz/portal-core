/*
 * This file is part of the AuScope Virtual Exploration Geophysics Lab (VEGL) project.
 * Copyright (c) 2011 CSIRO Earth Science and Resource Engineering
 *
 * Licensed under the terms of the GNU Lesser General Public License.
 */
Ext.namespace("ScriptBuilder");
Ext.ux.ComponentLoader.load( {url : ScriptBuilder.componentPath + "VEGLJobObject.json"});

VEGLJobObjectNode = Ext.extend(ScriptBuilder.BasePythonComponent, {

    constructor : function(container) {
        VEGLJobObjectNode.superclass.constructor.apply(this, [ container,
                "VEGL Job Object", "VEGLJobObject", "s" ]);

        var numShells = container.getShellCommands().length;
        this.values.uniqueName = "shell" + numShells;
    },
    
    /**
     * This is where we dynamically generate a python Getter/Setter class from the job object that
     * is sent to us 
     */
    getScript : function() {
        var classText = '';
        
        //Generate our utility VEGLBBox class
        classText += '# Autogenerated Getter/Setter class' + this._newLine;
        classText += this._popoClass('VEGLBBox', ['srs', 'maxNorthing', 'minNorthing', 'maxEasting', 'minEasting']);
        classText += this._tab + '# Returns true if the specified northing/easting (assumed to be in the same SRS)' + this._newLine;
        classText += this._tab + '# lies within the spatial area represented by this bounding box. ' + this._newLine;
        classText += this._tab + 'def isPointInsideArea(self, northing, easting):' + this._newLine;
        classText += this._tab + this._tab + 'return ((easting >= self._minEasting) and (easting <= self._maxEasting) and (northing >= self._minNorthing) and (northing <= self._maxNorthing))' + this._newLine;
        classText += this._newLine;
        
        //Iterate our fields to figure out which ones we want to include
        var fieldsToInclude = [];
        for (var field in this.values) {
            var value = this.values[field];
            if (Ext.isFunction(value)) {
                //Ignore functions
            } else if (Ext.isObject(value)) {
                //Ignore complex fields for the moment
            } else if (Ext.isPrimitive(value)) {
                //Primitive fields turn into 'Getters'
                fieldsToInclude.push(field);
            }
        }
        //Generate our getter/setter class
        classText += '# Autogenerated Getter/Setter class' + this._newLine;
        classText += this._popoClass('VEGLParameters', fieldsToInclude);
        classText += this._tab + '# Gets an instance of VEGLBBox representing the padded bounds' + this._newLine;
        classText += this._tab + 'def getPaddedBounds(self):' + this._newLine;
        classText += this._tab + this._tab + 'return VEGLBBox(srs=self._mgaZone, maxNorthing=self._paddingMaxNorthing, maxEasting=self._paddingMaxEasting, minNorthing=self._paddingMinNorthing, minEasting=self._paddingMinEasting)' + this._newLine;
        classText += this._newLine;
        classText += this._tab + '# Gets an instance of VEGLBBox representing the padded bounds' + this._newLine;
        classText += this._tab + 'def getSelectedBounds(self):' + this._newLine;
        classText += this._tab + this._tab + 'return VEGLBBox(srs="EPSG:4326", maxNorthing=self._selectionMaxNorthing, maxEasting=self._selectionMaxEasting, minNorthing=self._selectionMinNorthing, minEasting=self._selectionMinEasting)' + this._newLine;
        classText += this._newLine;
        
        //Instantiate our getter/setter class
        classText += '# Global parameter instance for reference' + this._newLine;
        classText += 'VEGLParams = VEGLParameters(';
        for (var i = 0; i < fieldsToInclude.length; i++) {
            var field = fieldsToInclude[i];
            var value = this.values[field];
            classText += field + '=' + this._getPrimitiveValue(value);
            if (i < (fieldsToInclude.length - 1)) {
                classText += ', ';
            }
        }
        classText += ')' + this._newLine;
            
        
        classText += this._newLine;
        
        return classText;
    }
});
