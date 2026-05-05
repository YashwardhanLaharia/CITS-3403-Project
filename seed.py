import sys
from datetime import datetime, date
from random import choice, uniform

sys.path.insert(0, '.')

from app import create_app
from extensions import db
from models import User, Group, Membership, Expense


def seed():
    app = create_app('development')
    with app.app_context():
        db.drop_all()
        db.create_all()

        user1 = User(
            email='alice@example.com',
            password_hash='hashed_password_1',
            first_name='Alice',
            last_name='Anderson'
        )
        user2 = User(
            email='bob@example.com',
            password_hash='hashed_password_2',
            first_name='Bob',
            last_name='Baker'
        )
        user3 = User(
            email='charlie@example.com',
            password_hash='hashed_password_3',
            first_name='Charlie',
            last_name='Cox'
        )
        db.session.add_all([user1, user2, user3])
        db.session.commit()

        group = Group(
            name='Summer Roadtrip',
            currency='AUD',
            invite_code='SRD24AUD',
            created_by=user1.id
        )
        db.session.add(group)
        db.session.commit()

        membership1 = Membership(
            user_id=user1.id,
            group_id=group.id,
            role='admin'
        )
        membership2 = Membership(
            user_id=user2.id,
            group_id=group.id,
            role='member'
        )
        membership3 = Membership(
            user_id=user3.id,
            group_id=group.id,
            role='member'
        )
        db.session.add_all([membership1, membership2, membership3])

        expenses = [
            Expense(
                group_id=group.id,
                paid_by=user1.id,
                description='Petrol',
                amount=60.00,
                category='transport',
                date=date(2024, 7, 1)
            ),
            Expense(
                group_id=group.id,
                paid_by=user2.id,
                description='Groceries',
                amount=45.50,
                category='food',
                date=date(2024, 7, 2)
            ),
            Expense(
                group_id=group.id,
                paid_by=user3.id,
                description='Hotel',
                amount=150.00,
                category='accommodation',
                date=date(2024, 7, 3)
            ),
            Expense(
                group_id=group.id,
                paid_by=user1.id,
                description='Dinner',
                amount=85.00,
                category='food',
                date=date(2024, 7, 4)
            ),
            Expense(
                group_id=group.id,
                paid_by=user2.id,
                description='Museum tickets',
                amount=30.00,
                category='entertainment',
                date=date(2024, 7, 5)
            ),
        ]
        db.session.add_all(expenses)
        db.session.commit()

        print('Seeded: 3 users, 1 group, 3 memberships, 5 expenses')
        print(f'Group invite code: {group.invite_code}')


if __name__ == '__main__':
    seed()