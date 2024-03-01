from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Notas, Boletim

@receiver(post_save, sender=Notas)
def associar_notas_a_boletim(sender, instance, created, **kwargs):
    if created:
        # Verificar se já existe um boletim para o aluno e a aula da nota
        boletim_existente = Boletim.objects.filter(aluno=instance.aluno, curso=instance.aula.capitulo.curso, capitulo=instance.aula.capitulo, aula=instance.aula).exists()

        if not boletim_existente:
            # Se não existir, criar um novo boletim para o aluno e a aula da nota
            novo_boletim = Boletim(aluno=instance.aluno, curso=instance.aula.capitulo.curso, capitulo=instance.aula.capitulo, aula=instance.aula)
            novo_boletim.save()

        # Adicionar a nota ao boletim do aluno e aula da nota
        boletim = Boletim.objects.get(aluno=instance.aluno, curso=instance.aula.capitulo.curso, capitulo=instance.aula.capitulo, aula=instance.aula)
        boletim.notas.add(instance)
