import re
from django.shortcuts import render
from rest_framework import viewsets
from .models import *
from .serializers import *
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.views.decorators.csrf import csrf_exempt
from rest_framework.response import Response
from rest_framework.decorators import api_view
import json
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.shortcuts import get_object_or_404





# EndPoint to get the certifications
class CertificationList(APIView):
    
    # DEFINIR EL METODO GET QUE SE REALIZA DESDE EL FRONT    
    def get(self, request):
        
        # Queryset de las certificaciones
        certifications_queryset = Certificaciones.objects.all()
        serializer = CertificationSerializer(certifications_queryset, many = True)
        # RETORNA LOS DATOS EN JSON
        #(serializer.data)
        return Response(serializer.data)
    
    

@csrf_exempt
@api_view(['POST'])
def receive_tags(request):
    if request.method == 'POST':
        tags = request.data.get('tags', [])
        if not isinstance(tags, list):
            return Response({"Error": "Formato de datos invalido"}, status=status.HTTP_400_BAD_REQUEST)
        
        
        if not all(isinstance(tag, str) for tag in tags):
            return Response({"Error": "Cada tag debe ser una cadena de texto"}, status=status.HTTP_400_BAD_REQUEST)
        
        print(f"Tags recibidos: {tags}")
        
        
        return Response({"message": "Tags recibidos correctamente"}, status = status.HTTP_200_OK)
    
    return Response({"error": "Metodo no permitido"}, status=status.HTTP_405_METHOD_NOT_ALLOWED)




    
  
  
#EndPoint to get the skills  
class SkillsList (APIView):
    
    def get(self, request):
        
        #Queryset of the skills
        skills = Habilidades.objects.all()
        skills_serializer = SkillsSerializer(skills, many= True)
        
        return Response (skills_serializer.data)
    

# EndPoint to get the Universities
class UniversitiesList (APIView):
    
    def get(self, request):
        
        #Queryset of the Universities
        universities = Universidades.objects.all()
        universities_serializer = UniverisitiesSerializer(universities, many= True)
        
        return Response(universities_serializer.data)


class TopicsList (APIView):
    
    def get(self, request):
        
        #Queryset of the Topics
        topics =  Temas.objects.all()
        topics_serializer = TopicsSerializer(topics, many = True)
        
        return Response(topics_serializer.data)
    


# Esta función obtiene el id de la certificación que el usuario quiere ver en vista especifica y retorna toda su información
@api_view(['GET'])
def get_certification(request, id):
    try:
        # Validar que el id existe
        if not id:
            return Response(
                {'Error': 'Se requiere el ID de la certificación'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Obtener la certificación   
        certification = Certificaciones.objects.get(id=id)
        
        # Separar cada instructor y formatear para mayor facilidad de mostrar en el front
        certification_instructors = certification.certification_instructors.split('\n')
        instructor_links = []
        
        # regex para separar link del nombre
        regex = re.compile(r'^([^,]+),\s*(https?:\/\/[^\s,]+),')
            
        
        for line in certification_instructors:
            match = regex.match(line)
            if match:
                name = match.group(1)
                link = match.group(2)
                
                # Diccionario con nombre y link
                instructor_links.append({
                    'name': name,
                    'link': link
                })
        
        # Serializar y retornar
        serializer = CertificationSerializer(certification)
        data = serializer.data
        
        
        
        data['certification_instructors'] = instructor_links
        
    
        #Separar items de aprendizaje
        certification_learnings = certification.certification_learnings.split('\n')        
        
        data['certification_learnings'] = certification_learnings
        
        
        #Separar habilidades
        certification_skills = certification.certification_skills.split('-')
        
        data['certification_skills'] = certification_skills
        
        # Retornar los datos de la certificación
        return Response(data)
        

        
    except Certificaciones.DoesNotExist:
        return Response(
            {'error': 'Certificación no encontrada'},
            status=status.HTTP_404_NOT_FOUND
        )
    except ValueError:
        return Response(
            {'error': 'ID Invalido'},
            status=status.HTTP_400_BAD_REQUEST
        )


# Esta funcion sirve para recibir los tags por los cuales el ususario quiere filtrar las busquedas y retornar el queryset con las certificaciones filtradas
@csrf_exempt
@require_http_methods(["POST"])
def filter_by_tags(request):
        try: 
            # Peticion del body 
            data = json.loads(request.body)
            
            # Diccionario para almacenar los tags seleccionados por el usuario     
            categories_dict = {
                'Temas': set(),
                'Universidades': set(),
                'Plataformas': set(),
                'Empresas': set(),
                'Habilidades': set()
            }
            
            category_models = {
                'Temas': Temas,
                'Universidades': Universidades,
                'Plataformas': Plataformas,
                'Empresas': Empresas,
                'Habilidades': Habilidades
            }
            
            # Este diccionario es para convertir el nombre de la categoria a el nombre de la columna que contiene el id de la categoriaen la tabla certificaciones
            
            category_db_filtered = {
                'Temas': 'tema_certificacion_id',
                'Universidades': 'universidad_certificacion_id',
                'Plataformas': 'plataforma_certificacion_id'
            }
            

            #Iterar sobre data(Enviado por el front) para almacenar cada tag en su categoria dentro del dicccionario
            for categoria, tag in data.items():
                if isinstance(tag, list):
                    categories_dict[categoria].update(tag)
                else:
                    categories_dict[categoria].add(tag)
            #print(categories_dict) 
            
            
            # En este diccionario se usara para almacenar las categorias con tags seleccionados, y poder sacar las query set
            non_empty_categories = {
                categoria: tag
                for categoria, tags in categories_dict.items()
                if tags # Condición que veriifica cuales tienen tags seleccionados
            }
            
            # Este for sirve para generar un query set sobre las categorias que tienen tags seleecionados
            for category, tag in non_empty_categories.items():
                for i in tag:
                    # Se obtiene el objeto de acuerdo al nombre del tag
                    category_uf= get_object_or_404(category_models.get(category), nombre=i)
                    # Se genera una consulta a la base de datos 
                    filtered_queryset = Certificaciones.objects.filter(**{category_db_filtered.get(category): category_uf.id})
                    print(f"Filtrando por {category_uf}")
                    print(filtered_queryset)
            
            
            
           
            
            
            
            
       
            return JsonResponse({
                # Devolver sun estado success
               'status': 'success'
                })
        
        # Manejo de errores
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON'}, status=400)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
        

        