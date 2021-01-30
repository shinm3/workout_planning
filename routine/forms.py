from django import forms
from .models import BodyPart, TermDecision


class BodyPartForm(forms.ModelForm):

    class Meta:
        model = BodyPart
        fields = [
            'week',
            'part',
            'detail_part',
        ]

    def __init__(self, *args, **kwargs):
        if 'bp_objects' in kwargs:
            self.bp_objects = kwargs.pop('bp_objects')
        else:
            self.bp_objects = None
        super(BodyPartForm, self).__init__(*args, **kwargs)

    def clean(self):
        """ 同じ部位が選択されたかどうかのバリデーションになります。 """
        cleaned_data = super().clean()
        part = cleaned_data.get('part')
        detail_part = cleaned_data.get('detail_part')
        if detail_part == '部位の詳細':
            raise forms.ValidationError("同じ部位は登録できません")
        print(self.bp_objects)
        if self.bp_objects:
            for bp_object in self.bp_objects:
                if part == bp_object['part'] and detail_part == bp_object['detail_part']:
                    raise forms.ValidationError("同じ部位は登録できません")
            return cleaned_data

    def clean_part(self):
        part = self.cleaned_data.get('part')
        if part is None:
            raise forms.ValidationError("部位を選択してください")
        return part


class TermDecisionForm(forms.ModelForm):

    class Meta:
        model = TermDecision
        fields = [
            'start_date',
            'end_date',
        ]
        widgets = {
            'start_date': forms.SelectDateWidget,
            'end_date': forms.SelectDateWidget
        }
