from django.shortcuts import render
from django.http import JsonResponse
from systemsdep_ui import utils
from systemsdep_ui.utils import get_all_systems_from_neptune
from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json 
# Create your views here.

def neptune_visualization_view(request):
    # Additional context data can be added here if needed

    neptune_edges = utils.get_neptune_data()
    distinct_labels = utils.get_distinct_labels_from_neptune()
    all_systems = get_all_systems_from_neptune()
    
    return render(request, 'systemsdep_ui/index.html', 
                 context={
                    'distinct_labels':distinct_labels, 
                    'edges': neptune_edges,
                    'all_systems': all_systems
                })

def gremlin_search(request):
    # Retrieve the node value from the request parameters
    node_value = request.GET.get('node')

    # print(node_value)
    # Perform the Gremlin search query using node_value and get the results
    gremlin_query_result = utils.perform_gremlin_query(node_value)

    return JsonResponse(gremlin_query_result, safe=False)



# handles the creation of a new dependency between two systems in the Neptune database
def add_dependency_view(request):
    if request.method == "POST":
        data = json.loads(request.body)
        # print(data)
        source_system_name = data.get("source_system_name")
        destination_system_name = data.get("destination_system_name")
        data_object = data.get("data_object")
        integration_type = data.get("integration_type")
        platform_type = data.get("platform_type")  
        implementation_type = data.get("implementation_type")  
        tech_lead = data.get("tech_lead")  
        description = data.get("description") 

        if source_system_name and destination_system_name and data_object and integration_type:
            success, updated_data = utils.add_dependency_to_neptune(source_system_name, destination_system_name, data_object, integration_type, platform_type, implementation_type, tech_lead, description)
            if success:
                return JsonResponse({"success": True, "updated_data": updated_data})
            else:
                return JsonResponse({"success": False, "error": updated_data})
    else:
        distinct_labels = utils.get_distinct_labels_from_neptune()
        return render(request, 'systemsdep_ui/addDependency.html', {'distinct_labels': distinct_labels})
    return JsonResponse({"success": False, "error": "Invalid request method."})


def add_system_view(request):
    if request.method == "POST":
        system_name = json.loads(request.body).get("system_name")
        if system_name:
            # Call a function to add the new system to the Neptune database
            success, updated_data = utils.add_system_to_neptune(system_name)
            if success:
                return JsonResponse({"success": True, "updated_data": updated_data})
            else:
                return JsonResponse({"success": False, "error": "Failed to add the system to the database."})
    else:
        distinct_labels = utils.get_distinct_labels_from_neptune()
        return render(request, 'systemsdep_ui/addSystem.html', {'distinct_labels': distinct_labels})
    return JsonResponse({"success": False, "error": "Invalid request method."})



def edit_system_view(request):
    if request.method == "POST":
        edited_system_name = json.loads(request.body).get("edited_system_name")
        existing_system_id = json.loads(request.body).get("existing_system_id")
        #print(edited_system_name, existing_system_id)
        if edited_system_name:
            # Call a function to add the new system to the Neptune database
            success, updated_data = utils.edit_system_to_neptune(existing_system_id,edited_system_name)
            if success:
                return JsonResponse({"success": True, "updated_data": updated_data})
            else:
                return JsonResponse({"success": False, "error": "Failed to add the system to the database."})
    else:
        distinct_labels = utils.get_distinct_labels_from_neptune()
        all_systems = get_all_systems_from_neptune()
        return render(request, 'systemsdep_ui/editSystem.html', {'distinct_labels': distinct_labels, 'all_systems': all_systems})
    return JsonResponse({"success": False, "error": "Invalid request method."})



def delete_system_view(request):
    if request.method == "POST":
        system_id = json.loads(request.body).get("system_id")
        if system_id:
            success, message = utils.delete_system_from_neptune(system_id)
            if success:
                return JsonResponse({"success": True, "message": message})
            else:
                return JsonResponse({"success": False, "error": message})
    else:
        all_systems = get_all_systems_from_neptune()
        return render(request, 'systemsdep_ui/deleteSystem.html', {'all_systems': all_systems})
    return JsonResponse({"success": False, "error": "Invalid request method."})