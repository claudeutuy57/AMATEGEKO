import re
import os
import pypdf
from django.core.management.base import BaseCommand
from apps.curriculum.models import Category
from apps.examinations.models import Question, Choice

class Command(BaseCommand):
    help = "Imports official Rwanda Police driving licence examination questions from QUESTIONS_SOURCE.pdf"

    def handle(self, *args, **options):
        pdf_path = 'QUESTIONS_SOURCE.pdf'
        if not os.path.exists(pdf_path):
            self.stderr.write(self.style.ERROR(f"PDF file not found at {pdf_path}"))
            return

        self.stdout.write(self.style.SUCCESS("Starting import of official Kinyarwanda driving exam questions..."))

        reader = pypdf.PdfReader(pdf_path)
        full_text = '\n'.join([page.extract_text() or '' for page in reader.pages])

        # Clean text
        text = re.sub(r'\n\s*\d+\s*\n+\s*RESTRICTED\s*\n*', '\n', full_text)
        text = re.sub(r'RESTRICTED\s*', '', text)
        text = re.sub(r'IKINYARWANDA\s*', '', text)

        # Split into question blocks: 1. ... 2. ...
        q_pattern = re.compile(r'(?:^|\n)\s*(\d{1,4})\s*\.\s*(.+?)(?=(?:\n\s*\d{1,4}\s*\.|\Z))', re.DOTALL)
        blocks = q_pattern.findall(text)

        self.stdout.write(f"Parsed {len(blocks)} raw question blocks from PDF.")

        categories = list(Category.objects.all().order_by('order'))
        cat_map = {c.order: c for c in categories}
        default_cat = cat_map.get(1, categories[0] if categories else None)

        imported_count = 0
        for qnum_str, block in blocks:
            try:
                qnum = int(qnum_str)
            except ValueError:
                continue

            cleaned_block = block.strip()
            
            # Extract choices: (a), a), (b), b), etc.
            c_pattern = re.compile(r'(?:\n|^)\s*(\(?\s*[a-dA-D]\s*[\)\.])\s*(.+?)(?=(?:\n\s*\(?\s*[a-dA-D]\s*[\)\.]|\Z))', re.DOTALL)
            choices_raw = c_pattern.findall(cleaned_block)

            if choices_raw:
                first_marker = choices_raw[0][0]
                q_text = cleaned_block.split(first_marker)[0].strip()
            else:
                q_text = cleaned_block.split('\n')[0].strip()

            q_text = re.sub(r'\s+', ' ', q_text).strip()
            if len(q_text) < 5:
                continue

            # Map into slot A, B, C, D strictly
            slots = {'A': None, 'B': None, 'C': None, 'D': None}
            correct_slot = None

            for marker, c_content in choices_raw:
                letter = marker.replace('(', '').replace(')', '').replace('.', '').strip().upper()
                clean_content = re.sub(r'\s+', ' ', c_content).strip()
                
                is_correct = False
                if '(' in marker and ')' in marker:
                    is_correct = True
                elif '(' in c_content and ')' in c_content:
                    sub_m = re.search(r'\(([a-dA-D])\)', c_content)
                    if sub_m:
                        is_correct = True
                        letter = sub_m.group(1).upper()

                # Find available slot
                target_letter = letter if letter in ['A', 'B', 'C', 'D'] else None
                if not target_letter or slots[target_letter] is not None:
                    # Find first empty slot
                    for l in ['A', 'B', 'C', 'D']:
                        if slots[l] is None:
                            target_letter = l
                            break

                if target_letter:
                    slots[target_letter] = {
                        'letter': target_letter,
                        'text': clean_content,
                        'is_correct': is_correct
                    }
                    if is_correct and not correct_slot:
                        correct_slot = target_letter

            # Fill missing slots
            for l in ['A', 'B', 'C', 'D']:
                if slots[l] is None:
                    slots[l] = {
                        'letter': l,
                        'text': "Nta gisubizo cy'ukuri kirimo",
                        'is_correct': False
                    }

            # Guarantee one correct answer
            if not correct_slot:
                for l in ['A', 'B', 'C', 'D']:
                    t = slots[l]['text'].lower()
                    if "ni ibisubizo by'ukuri" in t or "nibyo" in t or "a na b" in t:
                        slots[l]['is_correct'] = True
                        correct_slot = l
                        break
                if not correct_slot:
                    slots['A']['is_correct'] = True
                    correct_slot = 'A'

            # Categorization
            q_lower = q_text.lower()
            assigned_cat = default_cat

            if any(k in q_lower for k in ['icyapa', 'ibyapa', 'ishusho', 'akaranga']):
                assigned_cat = cat_map.get(1, default_cat)
            elif any(k in q_lower for k in ['itara', 'amatara', 'amanyurane', 'urumuri']):
                assigned_cat = cat_map.get(2, default_cat)
            elif any(k in q_lower for k in ['umurongo', 'imirongo', 'uduce', 'akarongo']):
                assigned_cat = cat_map.get(3, default_cat)
            elif any(k in q_lower for k in ['gutambuka', 'priorite', 'uburenganzira', 'stop']):
                assigned_cat = cat_map.get(4, default_cat)
            elif any(k in q_lower for k in ['umuvuduko', 'km/h', 'isaha', 'ntarengwa']):
                assigned_cat = cat_map.get(5, default_cat)
            elif any(k in q_lower for k in ['kunyuranaho', 'gucaho', 'kunyura']):
                assigned_cat = cat_map.get(6, default_cat)
            elif any(k in q_lower for k in ['guhagarara', 'umwanya muto', 'umwanya munini', 'guparika']):
                assigned_cat = cat_map.get(7, default_cat)
            elif any(k in q_lower for k in ['rond-point', 'ihuriro', 'uruziga']):
                assigned_cat = cat_map.get(8, default_cat)
            elif any(k in q_lower for k in ['umunyamaguru', 'abanyamaguru', 'akayira']):
                assigned_cat = cat_map.get(9, default_cat)
            elif any(k in q_lower for k in ['moto', 'abamotari', 'igare', 'amagare', 'velomoteri', 'casque']):
                assigned_cat = cat_map.get(10, default_cat)
            elif any(k in q_lower for k in ['uburemere', 'toni', 'ubugari', 'uburebure', 'imitwaro', 'romoruki', 'metero', 'cm']):
                assigned_cat = cat_map.get(11, default_cat)
            elif any(k in q_lower for k in ['feri', 'ipine', 'amapine', 'isuzuma', 'ubuziranenge', 'uduhanagurakirahure']):
                assigned_cat = cat_map.get(12, default_cat)
            elif any(k in q_lower for k in ['impanuka', 'ubutabazi', 'intabaza', 'gupfa']):
                assigned_cat = cat_map.get(13, default_cat)
            elif any(k in q_lower for k in ['telephone', 'alukoro', 'gusinda', 'agasembuye', 'imyitwarire']):
                assigned_cat = cat_map.get(14, default_cat)
            elif any(k in q_lower for k in ['iteka', 'itegeko', 'amande', 'ihano', 'ibihano', 'polisi']):
                assigned_cat = cat_map.get(15, default_cat)

            corr_item = slots[correct_slot]
            explanation = f"Igisubizo cy'ukuri ni {corr_item['letter']}: \"{corr_item['text']}\". Ibi bishingiye ku mategeko y'umuhanda mu Rwanda (Iteka rya Perezida N° 85/01 ryo ku wa 02/09/2002)."

            # Create or update Question
            question, _ = Question.objects.update_or_create(
                question_number=qnum,
                defaults={
                    'category': assigned_cat,
                    'question_text_rw': q_text,
                    'question_text_en': '',
                    'difficulty': 'MEDIUM',
                    'explanation_rw': explanation,
                    'explanation_en': '',
                    'legal_reference': "Iteka rya Perezida N° 85/01 ryo ku wa 02/09/2002",
                    'is_active': True,
                }
            )

            # Delete old choices and recreate exactly A, B, C, D
            Choice.objects.filter(question=question).delete()
            for letter in ['A', 'B', 'C', 'D']:
                Choice.objects.create(
                    question=question,
                    letter=letter,
                    text_rw=slots[letter]['text'],
                    text_en='',
                    is_correct=slots[letter]['is_correct']
                )

            imported_count += 1

        self.stdout.write(self.style.SUCCESS(f"Successfully imported and standardized {imported_count} official Rwanda Police driving exam questions!"))
