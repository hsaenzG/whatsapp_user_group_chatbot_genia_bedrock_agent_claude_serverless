import boto3
import os

dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table(os.environ.get('faqs_table'))

# Ejemplo de FAQs a insertar
faqs = [
    {
        'id_event': 1,
        'question': '¿Para quién es el AWS Community Day Guatemala?',
        'answer': 'El AWS Community Day Guatemala está dirigido a todas aquellas personas interesadas en aprender y compartir conocimientos sobre AWS. Este evento, creado "por la comunidad, para la comunidad", incluye discusiones técnicas, talleres y laboratorios prácticos, todos dirigidos por expertos y líderes de la industria.'
    },
    {
        'id_event': 1,
        'question': '¿Cuándo y dónde se llevará a cabo AWS Community Day Guatemala 2024?',
        'answer': 'El evento se llevará a cabo el 19 de Octubre en Universidad Rafael Landivar - Campus Central, ciudad de Guatemala.'
    },
    {
        'id_event': 1,
        'question': '¿En qué se diferencia AWS Community Day Guatemala de otras conferencias de la industria?',
        'answer': 'El AWS Community Day Guatemala destaca entre las conferencias del sector porque es un evento auténtico, hecho por la comunidad y para la comunidad. Aquí, la prioridad no son los grandes discursos, sino la colaboración directa y el aprendizaje entre colegas. Los líderes y expertos comunitarios son quienes diseñan y conducen el contenido, cultivando un entorno acogedor y cercano, perfecto para compartir conocimientos y experiencias de manera significativa.'
    },
    {
        'id_event': 1,
        'question': '¿Puedo asistir al AWS Community Day Guatemala virtualmente?',
        'answer': '¡Claro! Podrás disfrutar en vivo de la keynote y las charlas sobre innovación a través de nuestra transmisión en directo, y si te las pierdes, estarán disponibles bajo demanda después del evento. Sin embargo, dado que el contenido del AWS Community Day Guatemala es altamente interactivo y pensado para la participación presencial, muchas de las sesiones de aprendizaje no estarán disponibles en formato virtual. ¡Te animamos a unirte en persona para vivir la experiencia completa!'
    },
    {
        'id_event': 1,
        'question': 'Estoy interesado en ser patrocinador del AWS Community Day Guatemala. ¿Puedo obtener más información?',
        'answer': 'Por supuesto, puedes obtener más información sobre cómo ser patrocinador enviando un mensaje por medio de este link: https://api.whatsapp.com/send?phone=50256536538&text=Hola%2C%20me%20interesa%20ser%20patrocinador%20para%20el%20evento%20del%20Community%20Day%20en%20Guatemala.'
    },
]

# Insertar FAQs en la tabla
with table.batch_writer() as batch:
    for faq in faqs:
        batch.put_item(Item=faq)