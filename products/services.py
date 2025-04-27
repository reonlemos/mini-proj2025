import stripe
from django.conf import settings
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from .models import PaymentTransaction

# Use the secret key for server-side operations
stripe.api_key = settings.STRIPE_SECRET_KEY

class PaymentService:
    @staticmethod
    def process_payment(bid):
        """
        Process payment for a winning bid using Stripe
        """
        try:
            # Create a payment transaction
            payment = PaymentTransaction.objects.create(
                bid=bid,
                amount=bid.amount
            )

            # Get the user's default payment method
            customer = stripe.Customer.retrieve(bid.user.stripe_customer_id)
            payment_method = customer.default_source

            if not payment_method:
                raise Exception("No default payment method found")

            # Create a payment intent
            intent = stripe.PaymentIntent.create(
                amount=int(bid.amount * 100),  # Convert to cents
                currency='inr',
                customer=customer.id,
                payment_method=payment_method,
                confirm=True,
                description=f"Payment for {bid.product.name} auction"
            )

            # Update payment transaction
            payment.transaction_id = intent.id
            payment.status = 'completed'
            payment.save()

            # Send email notification
            PaymentService.send_winner_notification(bid)

            return True, "Payment processed successfully"

        except stripe.error.CardError as e:
            payment.status = 'failed'
            payment.error_message = str(e)
            payment.save()
            return False, str(e)

        except Exception as e:
            payment.status = 'failed'
            payment.error_message = str(e)
            payment.save()
            return False, str(e)

    @staticmethod
    def send_winner_notification(bid):
        """
        Send email notification to the winner
        """
        subject = f"Congratulations! You won the auction for {bid.product.name}"
        
        # Prepare email context
        context = {
            'product_name': bid.product.name,
            'amount': bid.amount,
            'user_name': bid.user.name or bid.user.username
        }
        
        # Render email template
        html_message = render_to_string('products/email/winner_notification.html', context)
        plain_message = strip_tags(html_message)
        
        # Send email
        send_mail(
            subject=subject,
            message=plain_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[bid.user.email],
            html_message=html_message
        ) 