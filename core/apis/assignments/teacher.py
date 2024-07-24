from flask import Blueprint
from core import db
from core.apis import decorators
from core.apis.responses import APIResponse
from core.models.assignments import Assignment, AssignmentStateEnum
from .schema import AssignmentSchema, AssignmentGradeSchema

teacher_assignments_resources = Blueprint('teacher_assignments_resources', __name__)

@teacher_assignments_resources.route('/assignments', methods=['GET'], strict_slashes=False)
@decorators.authenticate_principal
def list_assignments(p):
    """Returns list of assignments"""
    teachers_assignments = Assignment.get_assignments_by_teacher()
    teachers_assignments = [a for a in teachers_assignments if a.teacher_id == p.teacher_id and a.state != AssignmentStateEnum.DRAFT.value]
    teachers_assignments_dump = AssignmentSchema().dump(teachers_assignments, many=True)
    return APIResponse.respond(data=teachers_assignments_dump)

@teacher_assignments_resources.route('/assignments/grade', methods=['POST'], strict_slashes=False)
@decorators.accept_payload
@decorators.authenticate_principal
def grade_assignment(p, incoming_payload):
    """Grade an assignment"""
    grade_assignment_payload = AssignmentGradeSchema().load(incoming_payload)
    
    assignment = Assignment.query.get(grade_assignment_payload.id)
    if not assignment:
        return APIResponse.respond(data={"error": "FyleError", "message": "Assignment not found"}, status=404)
    
    if assignment.teacher_id != p.teacher_id:
        return APIResponse.respond(data={"error": "Assignment not found or not authorized"}, status=400)
    
    if assignment.state != AssignmentStateEnum.SUBMITTED.value:
        return APIResponse.respond(data={"error": "Only submitted assignments can be graded"}, status=400)
    
    graded_assignment = Assignment.mark_grade(
        _id=grade_assignment_payload.id,
        grade=grade_assignment_payload.grade,
        auth_principal=p
    )
    db.session.commit()
    graded_assignment_dump = AssignmentSchema().dump(graded_assignment)
    return APIResponse.respond(data=graded_assignment_dump)
