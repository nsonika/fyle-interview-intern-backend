from flask import Blueprint
from core import db
from core.apis import decorators
from core.apis.responses import APIResponse
from core.models.assignments import Assignment, AssignmentStateEnum
from core.models.teachers import Teacher
from .schema import AssignmentSchema, TeacherSchema, AssignmentGradeSchema
from marshmallow import ValidationError
from core.libs import assertions

principal_assignments_resources = Blueprint('principal_assignments_resources', __name__)

@principal_assignments_resources.route('/assignments', methods=['GET'], strict_slashes=False)
@decorators.authenticate_principal
def list_assignments(principal):
    """Returns list of submitted and graded assignments for principal"""
    assignments = Assignment.query.filter(
        Assignment.state.in_([AssignmentStateEnum.SUBMITTED.value, AssignmentStateEnum.GRADED.value])
    ).all()
    assignments_dump = AssignmentSchema().dump(assignments, many=True)
    return APIResponse.respond(data=assignments_dump)

@principal_assignments_resources.route('/teachers', methods=['GET'], strict_slashes=False)
@decorators.authenticate_principal
def list_teachers(principal):
    """Returns list of teachers"""
    teachers = Teacher.get_teachers()
    teachers_dump = TeacherSchema().dump(teachers, many=True)
    return APIResponse.respond(data=teachers_dump)

@principal_assignments_resources.route('/assignments/grade', methods=['POST'], strict_slashes=False)
@decorators.accept_payload
@decorators.authenticate_principal
def grade_assignment(principal, payload):
    """Grade an assignment"""
    try:
        grade_data = AssignmentGradeSchema().load(payload)
        assignment = Assignment.query.get(grade_data.id)
        
        if assignment is None:
            return APIResponse.respond_error(message='Assignment not found', status_code=404)

        if assignment.state == AssignmentStateEnum.DRAFT.value:
            return APIResponse.respond_error(message='Cannot grade a draft assignment', status_code=400)
        
        graded_assignment = Assignment.mark_grade(
            _id=grade_data.id,
            grade=grade_data.grade,
            auth_principal=principal
        )
        db.session.commit()
        graded_assignment_dump = AssignmentSchema().dump(graded_assignment)
        return APIResponse.respond(data=graded_assignment_dump)
    except ValidationError as e:
        return APIResponse.respond_error(message=str(e), status_code=400)
    except Exception as e:
        return APIResponse.respond_error(message=str(e), status_code=500)
