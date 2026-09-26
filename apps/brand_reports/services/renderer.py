from django.template.loader import get_template
from django.core.files.base import ContentFile
from xhtml2pdf import pisa
from io import BytesIO

class ReportRenderer:
    @staticmethod
    def generate_pdf_from_html(template_src, context_dict, instance):
        """
        Renders a PDF from an HTML template and saves it to the instance file field.
        """
        template = get_template(template_src)
        html  = template.render(context_dict)
        result = BytesIO()
        
        # xhtml2pdf needs to know how to resolve static paths, but for simplicity
        # we can embed CSS directly in the HTML or use absolute paths for images
        pdf = pisa.pisaDocument(BytesIO(html.encode("UTF-8")), result)
        
        if not pdf.err:
            file_name = f"{instance.report_type.lower()}_v{instance.version}.pdf"
            instance.file.save(file_name, ContentFile(result.getvalue()), save=True)
            instance.status = 'READY'
            instance.save()
            return True
        else:
            instance.status = 'FAILED'
            instance.save()
            return False
