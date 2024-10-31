bl_info = {
    "name": "UR Custom Properties",
    "author": "Umar Razzaq",
    "version": (1, 4),
    "blender": (2, 80, 0),
    "location": "View3D > Sidebar > Custom Properties",
    "description": "Add and remove multiple custom properties from selected meshes",
    "category": "Object",
}

import bpy

class CustomPropertyItem(bpy.types.PropertyGroup):
    key: bpy.props.StringProperty(name="Key", default="")
    value: bpy.props.StringProperty(name="Value", default="")
    same_as_mesh_name: bpy.props.BoolProperty(name="Same as Mesh Name", default=False)

class UR_CustomProperties(bpy.types.Panel):
    bl_label = "Custom Properties"
    bl_idname = "VIEW3D_PT_custom_properties"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "Custom Properties"
    
    def draw(self, context):
        layout = self.layout
        props = context.scene.custom_props

        # Group for Adding Properties
        box_add = layout.box()
        box_add.label(text="Add Custom Properties", icon='ADD')
        box_add.prop(props, "want_add", toggle=True, text="Want to Add Properties")

        if props.want_add:
            box_add.operator("object.batch_add_property", text="Add Properties")
            box_add.operator("custom_property.add_entry", icon='ADD', text="Add New Property Entry")
            
            # Display list of custom properties for Adding
            for i, item in enumerate(props.custom_properties):
                row = box_add.box()
                row.prop(item, "key", text="Key")
                
                if not item.same_as_mesh_name:
                    row.prop(item, "value", text="Value")
                row.prop(item, "same_as_mesh_name", text="Same as Mesh Name")

                # Remove button for individual property entry
                remove_op = row.operator("custom_property.remove_entry", text="Remove Entry", icon='X')
                remove_op.index = i

        # Group for Removing Properties
        box_remove = layout.box()
        box_remove.label(text="Remove Custom Properties", icon='REMOVE')
        box_remove.prop(props, "want_remove", toggle=True, text="Want to Remove Properties")

        if props.want_remove:
            box_remove.operator("object.batch_remove_property", text="Remove Properties")
            box_remove.operator("object.hard_remove_properties", text="Hard Remove Properties", icon='X')

            # Display list of custom properties for Removing
            for i, item in enumerate(props.custom_properties):
                row = box_remove.box()
                row.prop(item, "key", text="Key to Remove")

                # Remove button for individual property entry
                remove_op = row.operator("custom_property.remove_entry", text="Remove Entry", icon='X')
                remove_op.index = i


class BatchAddPropertyOperator(bpy.types.Operator):
    bl_idname = "object.batch_add_property"
    bl_label = "Add Custom Properties"
    
    def execute(self, context):
        props = context.scene.custom_props
        self.report({'INFO'}, "Adding properties...")  # Loading message

        try:
            for obj in context.selected_objects:
                for item in props.custom_properties:
                    key = item.key
                    value = obj.name if item.same_as_mesh_name else item.value
                    obj[key] = value

            self.report({'INFO'}, "Properties added successfully!")  # Success message
        except Exception as e:
            self.report({'ERROR'}, f"Failed to add properties: {e}")  # Error message

        return {'FINISHED'}


class BatchRemovePropertyOperator(bpy.types.Operator):
    bl_idname = "object.batch_remove_property"
    bl_label = "Remove Custom Properties"
    
    def execute(self, context):
        props = context.scene.custom_props
        self.report({'INFO'}, "Removing properties...")  # Loading message

        try:
            for obj in context.selected_objects:
                for item in props.custom_properties:
                    key = item.key
                    if key in obj:
                        del obj[key]

            self.report({'INFO'}, "Properties removed successfully!")  # Success message
        except Exception as e:
            self.report({'ERROR'}, f"Failed to remove properties: {e}")  # Error message

        return {'FINISHED'}


class HardRemovePropertiesOperator(bpy.types.Operator):
    bl_idname = "object.hard_remove_properties"
    bl_label = "Hard Remove All Properties"

    def execute(self, context):
        # Loop over all selected objects
        for obj in context.selected_objects:
            if obj:
                # Get all custom properties of the object
                custom_keys = list(obj.keys())
                # Remove all custom properties except for built-in properties
                for key in custom_keys:
                    if key not in {"_RNA_UI", "cycles_visibility"}:  # Add exceptions for Blender internal keys if needed
                        del obj[key]
        
        self.report({'INFO'}, "All custom properties removed successfully!")  # Success message
        return {'FINISHED'}


class AddPropertyEntryOperator(bpy.types.Operator):
    bl_idname = "custom_property.add_entry"
    bl_label = "Add Custom Property Entry"

    def execute(self, context):
        props = context.scene.custom_props
        props.custom_properties.add()
        self.report({'INFO'}, "New property entry added!")  # Success message
        return {'FINISHED'}


class RemovePropertyEntryOperator(bpy.types.Operator):
    bl_idname = "custom_property.remove_entry"
    bl_label = "Remove Custom Property Entry"

    index: bpy.props.IntProperty()  # Property to store the index of the entry to remove

    def execute(self, context):
        props = context.scene.custom_props
        if 0 <= self.index < len(props.custom_properties):
            props.custom_properties.remove(self.index)
            self.report({'INFO'}, "Property entry removed!")  # Success message
        return {'FINISHED'}


class CustomPropertiesSettings(bpy.types.PropertyGroup):
    want_add: bpy.props.BoolProperty(name="Want Add", default=False)
    want_remove: bpy.props.BoolProperty(name="Want Remove", default=False)
    custom_properties: bpy.props.CollectionProperty(type=CustomPropertyItem)


def register():
    bpy.utils.register_class(CustomPropertyItem)
    bpy.utils.register_class(UR_CustomProperties)
    bpy.utils.register_class(BatchAddPropertyOperator)
    bpy.utils.register_class(BatchRemovePropertyOperator)
    bpy.utils.register_class(HardRemovePropertiesOperator)
    bpy.utils.register_class(AddPropertyEntryOperator)
    bpy.utils.register_class(RemovePropertyEntryOperator)
    bpy.utils.register_class(CustomPropertiesSettings)
    bpy.types.Scene.custom_props = bpy.props.PointerProperty(type=CustomPropertiesSettings)


def unregister():
    bpy.utils.unregister_class(CustomPropertyItem)
    bpy.utils.unregister_class(UR_CustomProperties)
    bpy.utils.unregister_class(BatchAddPropertyOperator)
    bpy.utils.unregister_class(BatchRemovePropertyOperator)
    bpy.utils.unregister_class(HardRemovePropertiesOperator)
    bpy.utils.unregister_class(AddPropertyEntryOperator)
    bpy.utils.unregister_class(RemovePropertyEntryOperator)
    bpy.utils.unregister_class(CustomPropertiesSettings)
    del bpy.types.Scene.custom_props


if __name__ == "__main__":
    register()
